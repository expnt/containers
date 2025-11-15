#!/bin/bash

set -eo pipefail

CONTAINER=""
ALL_CONTAINERS=false
REPO_OWNER=${GITHUB_REPOSITORY_OWNER:-$(whoami)}
REPO_OWNER=$(echo "$REPO_OWNER" | tr '[:upper:]' '[:lower:]' | tr -d '/' | sed 's/_/-/g')
CHECK_VERSION=false
PUSH=false
OUTPUT=false
MULTIPLATFORM=false
CI_MODE=${GITHUB_ACTIONS:-false}

usage() {
  cat << EOF
Usage: $0 [container] [options]

Containers:
  [container]    See the folders in the containers/ directory for options.
  If no container is specified, all containers will be built.

Options:
  -h, --help              Show this help message
  -c, --check-version     Check if build is needed (for CI)
  -o, --output            Output image to Docker (default: false)
  -m, --multiplatform     Build for multiple platforms (linux/amd64,linux/arm64)
  --repo-owner OWNER      Set repository owner (default: current user)

Note: Pushing to registry is handled by CI. Local builds only save to Docker.
EOF
  exit 0
}

parse_args() {
  if [[ $# -eq 0 ]] || [[ "$1" == -* ]]; then
    ALL_CONTAINERS=true
  else
    CONTAINER="$1"
    shift
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help) usage ;;
      -c|--check-version) CHECK_VERSION=true; shift ;;
      -p|--push) 
        if [[ "$CI_MODE" != true ]]; then
          echo "Error: --push is only available in CI mode. Use CI to push images to registry."
          exit 1
        fi
        PUSH=true; shift ;;
      -o|--output) OUTPUT=true; shift ;;
      -m|--multiplatform) MULTIPLATFORM=true; shift ;;
      --repo-owner)
        shift
        REPO_OWNER=$(echo "$1" | tr '[:upper:]' '[:lower:]' | tr -d '/' | sed 's/_/-/g')
        shift
        ;;
      *) echo "Error: Unknown option: $1"; usage ;;
    esac
  done
}

setup_build() {
  [[ ! -d "containers/$CONTAINER" ]] && { echo "Error: Container directory not found: containers/$CONTAINER"; exit 1; }
  
  local version_file="containers/$CONTAINER/versions.env"
  [[ ! -f "$version_file" ]] && { echo "Error: Version file not found: $version_file"; exit 1; }
  
  source "$version_file"
  
  [[ -z "$BASE_VERSION" ]] && { echo "Error: BASE_VERSION not set in $version_file"; exit 1; }
  
  if [[ -n "$PLUGIN_VERSION" ]]; then
    if [[ ! "$PLUGIN_VERSION" =~ ^v ]]; then
      PLUGIN_VERSION_TAG="v${PLUGIN_VERSION}"
    else
      PLUGIN_VERSION_TAG="${PLUGIN_VERSION}"
    fi
  fi
}

build_image() {
  if [[ "$CHECK_VERSION" == true ]]; then
    echo "REBUILD_NEEDED=true" >> "$GITHUB_OUTPUT"
    return 0
  fi
  
  local args=(
    --build-arg BASE_VERSION="$BASE_VERSION"
    --build-arg GITHUB_REPOSITORY_OWNER="$REPO_OWNER"
  )
  
  [[ -n "$PG_MAJOR" ]] && args+=(--build-arg PG_MAJOR="$PG_MAJOR")
  [[ -n "$PLUGIN_VERSION" ]] && args+=(--build-arg PLUGIN_VERSION="$PLUGIN_VERSION")
  [[ -n "$PLUGIN_VERSION_TAG" ]] && args+=(--build-arg PLUGIN_VERSION_TAG="$PLUGIN_VERSION_TAG")
  
  local target="build"
  if [[ "$PUSH" == true ]] || [[ "$MULTIPLATFORM" == true ]]; then
    target="build-multiplatform"
  fi
  
  local flags=()
  [[ "$PUSH" == true ]] && flags+=(--push)
  [[ "$CI_MODE" == true ]] && flags+=(--ci)
  if [[ "$CI_MODE" != true ]] && [[ "$PUSH" != true ]]; then
    [[ "$OUTPUT" == true ]] && flags+=(--output)
  fi
  
  echo "Building container: $CONTAINER"
  echo "Repository owner: $REPO_OWNER"
  echo "Base version: $BASE_VERSION"
  [[ -n "$PG_MAJOR" ]] && echo "PostgreSQL major version: $PG_MAJOR"
  [[ -n "$PLUGIN_VERSION" ]] && echo "Plugin version: $PLUGIN_VERSION"
  if [[ "$PUSH" == true ]] || [[ "$MULTIPLATFORM" == true ]]; then
    echo "Platforms: linux/amd64,linux/arm64"
  fi
  
  set +e  
  earthly "${flags[@]}" "${args[@]}" "./containers/$CONTAINER+$target"
  local build_result=$?
  set -e  
  
  if [[ $build_result -eq 0 ]]; then
    local image_tag=""
    if [[ -n "$PG_MAJOR" ]] && [[ -n "$PLUGIN_VERSION_TAG" ]]; then
      image_tag="${PG_MAJOR}-plugin-${PLUGIN_VERSION_TAG}"
    elif [[ -n "$PLUGIN_VERSION_TAG" ]]; then
      image_tag="plugin-${PLUGIN_VERSION_TAG}"
    elif [[ -n "$BASE_VERSION" ]]; then
      image_tag="${BASE_VERSION}"
    else
      image_tag="latest"
    fi
    echo "✅ Built container: $CONTAINER:$image_tag"
    return 0
  else
    echo "❌ Error: Build failed with exit code $build_result"
    return $build_result 
  fi
}

build_all_containers() {
  local containers=()
  
  for dir in containers/*/; do
    local container_name=$(basename "$dir")
    containers+=("$container_name")
  done
  
  if [[ ${#containers[@]} -eq 0 ]]; then
    echo "Error: No container directories found in containers/"
    exit 1
  fi
  
  echo "Building all containers: ${containers[*]}"
  local failed_containers=()
  
  for container in "${containers[@]}"; do
    echo -e "\n===== Building $container ====="
    CONTAINER="$container"
    setup_build
    if ! build_image; then
      failed_containers+=("$container")
    fi
  done
  
  echo -e "\n===== Build Summary ====="
  if [[ ${#failed_containers[@]} -eq 0 ]]; then
    echo "✅ All containers built successfully"
    return 0
  else
    echo "❌ Failed containers: ${failed_containers[*]}"
    return 1
  fi
}

main() {
  parse_args "$@"
  
  if [[ "$ALL_CONTAINERS" == true ]]; then
    build_all_containers
  else
    setup_build
    build_image
  fi
}

main "$@"