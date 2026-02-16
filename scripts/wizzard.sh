#! /bin/bash
set -e

source ../.env

remote_address=""
parent_dir="$(dirname "$(pwd)")"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -l|--local)
            [[ -n "$remote_address" && "$remote_address" = false ]] && {
                echo "Error: Can't specify both --local and --remote."
                exit 1
            }
            remote_address="http://127.0.0.1:5000"
            ;;
        -r|--remote)
            [[ -n "$remote_address" && "$remote_address" = true ]] && {
                echo "Error: Can't specify both --local and --remote."
                exit 1
            }
            remote_address="${REMOTE_TRANSLATOR_URL}"
            ;;
        -h|--help)
            echo "Usage: $0 [--local|--remote]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

if [[ -z "$remote_address" ]]; then
    echo "Choose service mode:"
    echo "  1) Local"
    echo "  2) Remote"
    read -rp "Enter choice (1/2): " choice

    case "$choice" in
        1|l|L|local|Local)
            remote_address="http://127.0.0.1:5000"
            ;;
        2|r|R|remote|Remote)
            remote_address="${REMOTE_TRANSLATOR_URL}"
            ;;
        *)
            echo "Invalid choice."
            exit 1
            ;;
    esac
fi

function printTitle() {
    local title="$1"
    local term_width=""
    
    term_width=$(tput cols)
    
    local title_length=${#title}
    local total_padding=$((term_width - title_length - 2))
    if (( total_padding < 0 )); then
        total_padding=0
    fi
    local pad_left=$((total_padding / 2))
    local pad_right=$((total_padding - pad_left))
    
    printf '\n'
    printf '%*s\n' "$term_width" '' | sed 's/ /─/g'
    printf '%*s %s %*s\n' "$pad_left" '' "$title" "$pad_right" ''
    printf '%*s\n' "$term_width" '' | sed 's/ /─/g'
    printf '\n'
}

printTitle "Remote address set to '$remote_address'"

current_service_order="N/A"
function createServiceOrder(){
    # response=$(curl -s -w "%{http_code}" -X POST -F "file=@$parent_dir/app_descriptors/application_composition.yaml" "$remote_address/uc3/deployments")
    response=$(curl -s -w "%{http_code}" -X POST -F "file=@$parent_dir/app_descriptors/uc3_descriptor.yaml" "$remote_address/uc3/deployments")
    
    http_code="${response: -3}"
    json_body="${response::-3}"

    if [[ "$http_code" != "200" && "$http_code" != "201" ]]; then
        echo "Error: HTTP $http_code"
        echo "Response:"
        echo "$json_body" | jq '.'
        current_service_order="N/A"
        return
    fi

    serviceOrderId=$(jq -r '.serviceOrderId' <<< "$response")
    if [[ -z "$serviceOrderId" ]]; then
        echo "Error: 'serviceOrderId' field not found in JSON"
        echo "Response:"
        echo "$json_body" | jq '.'
        current_service_order="N/A"
        return
    fi

    echo "$json_body" | jq '.'

    current_service_order="$serviceOrderId"
    echo "The serviceOrder created successfully, the reference ServiceOrderId set to '$current_service_order'"
}

function getServiceOrderStatus(){

    if [ "$current_service_order" = "N/A" ]; then
        echo "There is no reference 'ServiceOrderId' set. Please select:'CREATE' option first."
        return
    fi

    response=$(curl -s -w "%{http_code}" -X GET "$remote_address/uc3/deployments/$current_service_order")

    http_code="${response: -3}"
    json_body="${response::-3}"

    if [[ "$http_code" != "200" && "$http_code" != "201" ]]; then
        echo "Error: HTTP $http_code"
        echo "Response:"
        echo "$json_body" | jq '.'
        return
    fi

    echo "The JSON result body is:"
    echo "$json_body" | jq '.'

    do_you_want_to_re_run=true
    while $do_you_want_to_re_run; do
        echo ""
        read -rp "Do you want to re-run 'GET SERVICE ORDER STATUS'? (y/n): " answer
        echo ""

        case "$answer" in
            [yY])
                echo "Waiting for 30 seconds..."
                sleep 30
                getServiceOrderStatus
                ;;
            [nN])
                echo "The service order status has been retrieved."
                do_you_want_to_re_run=false
                ;;
            *)
                echo "Invalid input. Please enter y or n."
                ;;
        esac
    done
}

function deleteServiceOrder(){

    if [ "$current_service_order" = "N/A" ]; then
        echo "There is no reference 'ServiceOrderId' set. Please select:'CREATE' option first."
        return
    fi

    response=$(curl -s -w "%{http_code}" -X DELETE "$remote_address/uc3/deployments/$current_service_order")

    http_code="${response: -3}"
    json_body="${response::-3}"

    if [[ "$http_code" != "200" && "$http_code" != "201" ]]; then
        echo "Error: HTTP $http_code"
        echo "Response:"
        echo "$json_body" | jq '.'
        return
    fi

    echo "The JSON result body is:"
    echo "$json_body" | jq '.'

    current_service_order="N/A"
}

function updateServiceOrder(){

    if [ "$current_service_order" = "N/A" ]; then
        echo "There is no reference 'ServiceOrderId' set. Please select:'CREATE' option first."
        return
    fi

    response=$(curl -s -w "%{http_code}" -X PATCH -F "file=@$parent_dir/app_descriptors/updated_uc3_descriptor.yaml" "$remote_address/uc3/deployments/$current_service_order")
    
    http_code="${response: -3}"
    json_body="${response::-3}"

    if [[ "$http_code" != "200" && "$http_code" != "201" ]]; then
        echo "Error: HTTP $http_code"
        echo "Response:"
        echo "$json_body" | jq '.'
        current_service_order="N/A"
        return
    fi

    echo "$json_body" | jq '.'

    current_service_order="$serviceOrderId"
    echo "The serviceOrder updated successfully"
}

while true; do

    printTitle "Current reference 'ServiceOrderId' is: '$current_service_order'"

    echo "Select an action:"
    echo "  1) CREATE SERVICE ORDER"
    echo "  2) GET SERVICE ORDER STATUS"
    echo "  3) UPDATE SERVICE ORDER"
    echo "  4) DELETE SERVICE ORDER"
    echo "  5) EXIT"
    read -rp "Enter choice (1/2/3/4/5): " action
    echo ""

    case "$action" in
        1|"create"|"CREATE")
            echo "CREATE SERVICE ORDER"
            createServiceOrder
            ;;
        2|"status"|"STATUS")
            echo "GET SERVICE ORDER STATUS"
            getServiceOrderStatus
            ;;
        3|"update"|"UPDATE")
            echo "UPDATING SERVICE ORDER"
            updateServiceOrder
            ;;

        4|"delete"|"DELETE")
            echo "DELETE SERVICE ORDER"
            deleteServiceOrder
            ;;
        5|"exit"|"EXIT")
            echo "Exiting"
            exit 0
            ;;
        *)
            echo "Invalid option."
            exit 1
            ;;
    esac
done
