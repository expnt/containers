#!/bin/bash

set -eo pipefail

CONTAINER=""
ALL_CONTAINERS=false
REPO_OWNER=${GITHUB_REPOSITORY_OWNER:-$(whoami)}
REPO_OWNER=$(echo "$REPO_OWNER" | tr '[:upper:]' '[:lower:]' | tr -d '/' | sed 's/_/-/g')
CHECK_VERSION=false
PUSH=false
OUTPUT=false
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
  -p, --push              Push image to registry
  -o, --output            Output image to Docker (default: false)
  --repo-owner OWNER      Set repository owner (default: current user)
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
      -p|--push) PUSH=true; shift ;;
      -o|--output) OUTPUT=true; shift ;;
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
  [[ -z "$PG_MAJOR" ]] && { echo "Error: PG_MAJOR not set in $version_file"; exit 1; }
  [[ -z "$PLUGIN_VERSION" ]] && { echo "Error: PLUGIN_VERSION not set in $version_file"; exit 1; }
  
  # Set PLUGIN_VERSION_TAG with v prefix if needed
  if [[ ! "$PLUGIN_VERSION" =~ ^v ]]; then
    PLUGIN_VERSION_TAG="v${PLUGIN_VERSION}"
  else
    PLUGIN_VERSION_TAG="${PLUGIN_VERSION}"
  fi
}

build_image() {
  if [[ "$CHECK_VERSION" == true ]]; then
    echo "REBUILD_NEEDED=true" >> "$GITHUB_OUTPUT"
    return 0
  fi
  
  local args=(
    --build-arg BASE_VERSION="$BASE_VERSION"
    --build-arg PG_MAJOR="$PG_MAJOR"
    --build-arg PLUGIN_VERSION="$PLUGIN_VERSION"
    --build-arg PLUGIN_VERSION_TAG="$PLUGIN_VERSION_TAG"
    --build-arg GITHUB_REPOSITORY_OWNER="$REPO_OWNER"
  )
  
  # Determine build target
  local target="build"
  [[ "$OUTPUT" == true ]] && target="docker"
  
  # Set build flags
  local flags=()
  [[ "$PUSH" == true ]] && flags+=(--push)
  [[ "$CI_MODE" == true ]] && flags+=(--ci)
  [[ "$target" == "docker" && "$CI_MODE" != true ]] && flags+=(--output)
  
  echo "Building container: $CONTAINER"
  echo "Repository owner: $REPO_OWNER"
  echo "Base version: $BASE_VERSION"
  echo "PostgreSQL major version: $PG_MAJOR"
  echo "Plugin version: $PLUGIN_VERSION"
  
  # Run earthly build
  set +e  
  earthly "${flags[@]}" "${args[@]}" "./containers/$CONTAINER+$target"
  local build_result=$?
  set -e  
  
  # Handle build result
  if [[ $build_result -eq 0 ]]; then
    local image_tag="${PG_MAJOR}-plugin-${PLUGIN_VERSION_TAG}"
    echo "✅ Built container: $CONTAINER:$image_tag"
    return 0
  else
    echo "❌ Error: Build failed with exit code $build_result"
    return $build_result 
  fi
}

build_all_containers() {
  local containers=()
  
  # Find all container directories
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
  
  # Build each container
  for container in "${containers[@]}"; do
    echo -e "\n===== Building $container ====="
    CONTAINER="$container"
    setup_build
    if ! build_image; then
      failed_containers+=("$container")
    fi
  done
  
  # Report results
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