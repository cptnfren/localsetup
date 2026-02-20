#!/bin/bash
# Localsetup v2 - OS detection

detect_os() {
    local os_type="" os_version="" architecture=""
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        os_type="linux"
        if [[ -f /etc/os-release ]]; then
            os_version=$(grep "^PRETTY_NAME=" /etc/os-release | cut -d'"' -f2)
        else
            os_version="Linux"
        fi
        architecture=$(uname -m)
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"
        os_version=$(sw_vers -productVersion 2>/dev/null || echo "Unknown")
        architecture=$(uname -m)
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ -n "${WINDIR:-}" ]]; then
        os_type="windows"
        os_version=$(powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption" 2>/dev/null || echo "Windows")
        architecture=$(uname -m 2>/dev/null || echo "x86_64")
    else
        os_type="unknown"
        os_version="Unknown"
        architecture=$(uname -m 2>/dev/null || echo "unknown")
    fi
    echo "$os_type|$os_version|$architecture"
}

cache_os_detection() {
    local engine_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    local user_data_dir
    user_data_dir=$(source "$engine_dir/lib/data_paths.sh" && get_user_data_dir)
    local cache_file="${user_data_dir}/config/detected_os.yaml"
    local os_info=$(detect_os)
    IFS='|' read -r os_type os_version architecture <<< "$os_info"
    mkdir -p "$(dirname "$cache_file")"
    cat > "$cache_file" << EOF
os: "$os_type"
version: "$os_version"
architecture: "$architecture"
detected_date: "$(date -u +"%Y-%m-%dT%H:%M:%S")"
EOF
}

get_cached_os() {
    local engine_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    local user_data_dir
    user_data_dir=$(source "$engine_dir/lib/data_paths.sh" && get_user_data_dir)
    local cache_file="${user_data_dir}/config/detected_os.yaml"
    if [[ -f "$cache_file" ]]; then
        grep "^os:" "$cache_file" | sed 's/^os:[[:space:]]*"\(.*\)"/\1/'
    else
        echo ""
    fi
}

validate_cached_os() {
    local cached_os=$(get_cached_os)
    local current_os_info=$(detect_os)
    IFS='|' read -r current_os _ _ <<< "$current_os_info"
    [[ -z "$cached_os" ]] && return 1
    [[ "$cached_os" != "$current_os" ]] && return 1
    return 0
}

export -f detect_os cache_os_detection get_cached_os validate_cached_os
