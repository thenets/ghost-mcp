#!/bin/bash

# create-release.sh
# Create a new GitHub release with the same version as the Python package.
#
# How to use:
#   This script reads the version from pyproject.toml and creates a GitHub release.
#   It checks that the 'github' remote exists and the version doesn't already exist.
#
# Example:
#   $ ./scripts/create-release.sh
#
# Requirements:
#   - git remote named 'github' must be configured
#   - gh CLI tool must be installed and authenticated
#   - Version in pyproject.toml must not already exist as a git tag
#
# NOTE:
#   Version tags and releases are immutable. If the version already exists,
#   the script will fail with an error.

# START


# Constants
declare -r SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
declare -r PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
declare -r PYPROJECT_FILE="$PROJECT_ROOT/pyproject.toml"


# Helpers
if [ -z "$TERM" ] || [ "$TERM" == "dumb" ]; then
    tput() {
        return 0
    }
fi
if ! type tput >/dev/null 2>&1; then
    tput() {
        return 0
    }
fi
function log_info() {
    local CYAN=$(tput setaf 6)
    local NC=$(tput sgr0)
    echo "${CYAN}[INFO   ]${NC} $*" 1>&2
}
function log_warning() {
    local YELLOW=$(tput setaf 3)
    local NC=$(tput sgr0)
    echo "${YELLOW}[WARNING]${NC} $*" 1>&2
}
function log_debug() {
    local PURPLE=$(tput setaf 5)
    local NC=$(tput sgr0)
    echo "${PURPLE}[DEBUG  ]${NC} $*" 1>&2
}
function log_error() {
    local RED=$(tput setaf 1)
    local NC=$(tput sgr0)
    echo "${RED}[ERROR  ]${NC} $*" 1>&2
}
function log_success() {
    local GREEN=$(tput setaf 2)
    local NC=$(tput sgr0)
    echo "${GREEN}[SUCCESS]${NC} $*" 1>&2
}
function log_title() {
    local GREEN=$(tput setaf 2)
    local BOLD=$(tput bold)
    local NC=$(tput sgr0)
    echo 1>&2
    echo "${GREEN}${BOLD}---- $* ----${NC}" 1>&2
}
function h_run() {
    local ORANGE=$(tput setaf 3)
    local NC=$(tput sgr0)
    echo "${ORANGE}\$ ${NC}$*" 1>&2
    eval "$*"
}
function err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}
function print_help() {
    # Prints help section from the top of the file
    #
    # It stops until it finds the '# START' line

    echo "HELP:"
    while read -r LINE; do
        if [[ "${LINE}" == "#!/bin/bash" ]] || [[ "${LINE}" == "" ]]; then
            continue
        fi
        if [[ "${LINE}" == "# START" ]]; then
            return
        fi
        echo "${LINE}" | sed 's/^# /  /g' | sed 's/^#//g'
    done <${BASH_SOURCE[0]}
}


# Functions
function check_requirements() {
    # Check if all required tools and configurations are available
    # Returns:
    #   0: All requirements met
    #   1: Missing requirements

    log_title "Checking Requirements"

    # Check if gh CLI is installed
    if ! command -v gh >/dev/null 2>&1; then
        log_error "GitHub CLI (gh) is not installed or not in PATH"
        log_info "Install it from: https://cli.github.com/"
        return 1
    fi
    log_info "✅ GitHub CLI found: $(gh --version | head -n1)"

    # Check if gh is authenticated
    if ! gh auth status >/dev/null 2>&1; then
        log_error "GitHub CLI is not authenticated"
        log_info "Run: gh auth login"
        return 1
    fi
    log_info "✅ GitHub CLI authenticated"

    # Check if github remote exists
    if ! git remote get-url github >/dev/null 2>&1; then
        log_error "Git remote 'github' is not configured"
        log_info "Configure it with: git remote add github <github-repo-url>"
        return 1
    fi
    local github_url
    github_url=$(git remote get-url github)
    log_info "✅ GitHub remote configured: $github_url"

    # Check if pyproject.toml exists
    if [[ ! -f "$PYPROJECT_FILE" ]]; then
        log_error "pyproject.toml not found at: $PYPROJECT_FILE"
        return 1
    fi
    log_info "✅ pyproject.toml found"

    return 0
}

function get_package_version() {
    # Extract version from pyproject.toml
    # Returns:
    #   Version string from pyproject.toml

    if [[ ! -f "$PYPROJECT_FILE" ]]; then
        log_error "pyproject.toml not found"
        return 1
    fi

    # Extract version using grep and sed
    local version
    version=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\([^"]*\)"/\1/')

    if [[ -z "$version" ]]; then
        log_error "Could not extract version from pyproject.toml"
        return 1
    fi

    echo "$version"
    return 0
}

function ensure_github_main_branch() {
    # Ensure we're working from the github/main branch
    # Returns:
    #   0: Successfully on github/main
    #   1: Failed to switch to github/main

    log_title "Ensuring GitHub Main Branch"

    # Fetch latest from github remote
    log_info "Fetching latest from github remote..."
    if ! h_run "git fetch github"; then
        log_error "Failed to fetch from github remote"
        return 1
    fi

    # Get current branch
    local current_branch
    current_branch=$(git branch --show-current)
    log_info "Current branch: $current_branch"

    # Check if we're already on a branch tracking github/main
    local upstream
    upstream=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "")

    if [[ "$upstream" != "github/main" ]]; then
        log_warning "Not on a branch tracking github/main (current upstream: ${upstream:-none})"

        # Check if we have uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            log_error "You have uncommitted changes. Please commit or stash them before creating a release."
            git status --short
            return 1
        fi

        # Switch to github/main
        log_info "Switching to github/main..."
        if ! h_run "git checkout -B release-temp github/main"; then
            log_error "Failed to checkout github/main"
            return 1
        fi
        log_info "✅ Now on branch tracking github/main"
    else
        # We're on a branch tracking github/main, make sure it's up to date
        log_info "Updating branch to match github/main..."
        if ! h_run "git reset --hard github/main"; then
            log_error "Failed to reset to github/main"
            return 1
        fi
        log_info "✅ Branch updated to match github/main"
    fi

    return 0
}

function check_version_exists() {
    # Check if version already exists as a git tag
    # Arguments:
    #   1: VERSION - version to check
    # Returns:
    #   0: Version does not exist (safe to create)
    #   1: Version already exists

    local VERSION=$1

    if [[ -z "$VERSION" ]]; then
        log_error "Version argument is required"
        return 1
    fi

    # Fetch tags from github remote to ensure we have latest
    log_info "Fetching tags from github remote..."
    if ! h_run "git fetch github --tags"; then
        log_error "Failed to fetch tags from github remote"
        return 1
    fi

    # Check if tag exists
    if git tag -l | grep -q "^v${VERSION}$"; then
        log_error "Version v${VERSION} already exists as a git tag"
        log_info "Existing tags:"
        git tag -l | grep -E "^v[0-9]" | sort -V | tail -5
        return 1
    fi

    log_info "✅ Version v${VERSION} does not exist yet"
    return 0
}

function create_github_release() {
    # Create GitHub release with tag
    # Arguments:
    #   1: VERSION - version to release
    # Returns:
    #   0: Release created successfully
    #   1: Failed to create release

    local VERSION=$1
    local TAG="v${VERSION}"

    if [[ -z "$VERSION" ]]; then
        log_error "Version argument is required"
        return 1
    fi

    log_title "Creating GitHub Release"

    # Create and push tag
    log_info "Creating tag: $TAG"
    if ! h_run "git tag $TAG"; then
        log_error "Failed to create tag $TAG"
        return 1
    fi

    log_info "Pushing tag to github remote..."
    if ! h_run "git push github $TAG"; then
        log_error "Failed to push tag to github remote"
        # Clean up local tag
        git tag -d "$TAG" 2>/dev/null || true
        return 1
    fi

    # Create GitHub release
    log_info "Creating GitHub release..."
    local release_notes="Release version $VERSION

This release includes all changes from the latest commits.

## Installation

\`\`\`bash
pip install ghost-mcp==$VERSION
\`\`\`

## What's Changed

See the [commit history](https://github.com/thenets/ghost-mcp/commits/v$VERSION) for detailed changes."

    if ! h_run "gh release create $TAG --title \"Release $VERSION\" --notes \"$release_notes\""; then
        log_error "Failed to create GitHub release"
        # Clean up tag
        git push github --delete "$TAG" 2>/dev/null || true
        git tag -d "$TAG" 2>/dev/null || true
        return 1
    fi

    log_success "🎉 GitHub release v$VERSION created successfully!"
    log_info "Release URL: https://github.com/thenets/ghost-mcp/releases/tag/$TAG"

    return 0
}


# Main
if [[ ${BASH_SOURCE[0]} == "${0}" ]]; then
    # Script is being invoked directly instead of being sourced

    # Handle help
    if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
        print_help
        exit 0
    fi

    # Change to project root
    cd "$PROJECT_ROOT" || {
        log_error "Failed to change to project root: $PROJECT_ROOT"
        exit 1
    }

    log_title "Ghost MCP Release Creator"

    # Check all requirements
    if ! check_requirements; then
        log_error "Requirements check failed"
        exit 1
    fi

    # Ensure we're on github/main branch
    if ! ensure_github_main_branch; then
        log_error "Failed to ensure github/main branch"
        exit 1
    fi

    # Get package version
    log_info "Reading version from pyproject.toml..."
    VERSION=$(get_package_version)
    if [[ $? -ne 0 ]] || [[ -z "$VERSION" ]]; then
        log_error "Failed to get package version"
        exit 1
    fi
    log_info "Package version: $VERSION"

    # Check if version already exists
    if ! check_version_exists "$VERSION"; then
        log_error "Version check failed"
        exit 1
    fi

    # Create the release
    if ! create_github_release "$VERSION"; then
        log_error "Failed to create GitHub release"
        exit 1
    fi

    log_success "Release creation completed successfully!"
fi