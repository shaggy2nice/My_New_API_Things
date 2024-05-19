#!/bin/bash

# Set the registry variable
harbor_registry="registry.io"

# Set the tag variable
tag_list_file="/tmp/$customer-tags.txt"

# Set the image variable
image_variable="image"

# Read the list of images from a file
image_list_file="/tmp/$customer-images.txt"

# Set current date
current_date=$(date +"%Y-%m-%d")


harbor_token=""

imageList_check(){
   # Check if the image list file exists
    tag_list_file="/tmp/$customer-tags.txt"
    image_list_file="/tmp/$customer-images.txt"
    if [ ! -f "$image_list_file" ]; then
        create_imageList
    fi
    echo "the image list is $image_list_file"
    echo "the tag list is $tag_list_file" 
}

create_imageList(){
    if [ -f "$image_list_file" ]; then
        rm $image_list_file
    fi
    echo "Creating image list for $customer"
    curl -X GET "https://$harbor_registry/api/v2.0/projects/$customer/repositories?page=1&page_size=100" -u $harbor_user:$harbor_token | jq > /tmp/$customer-temp.json && curl -X GET "https://$harbor_registry/api/v2.0/projects/$customer/repositories?page=2&page_size=100" -u $harbor_user:$harbor_token | jq >> /tmp/$customer-temp.json
    cat /tmp/$customer-temp.json | grep name | grep -v /cache | sed 's/.*"\([^"]*\)".*/\1/' | sed "s/$customer\///" > /tmp/$customer-images.txt && sort -o /tmp/$customer-images.txt /tmp/$customer-images.txt
    rm /tmp/$customer-temp.json
    echo "Image list creation complete"
}

copy_list(){
    cp /tmp/$customer-images.txt .
}

grab_images() {
   imageList_check
   # Grabbing image tags from harbor and creating a file to set tags as variables
   while IFS= read -r image || [ -n "$image" ]; do

      curl -X GET "https://$harbor_registry/api/v2.0/projects/$customer/repositories/${image}/artifacts/" -H 'accept: application/json' -u "$harbor_user:$harbor_token" | yq -p=json > /tmp/$customer-tags.yaml && yq eval '.[0].tags.[0].name' /tmp/$customer-tags.yaml >> /tmp/$customer-tags.txt

   done < "$image_list_file"
}

cleanup() {
    grab_images
    echo "the customer is $customer"
    echo "the image list is $image_list_file"
    echo "the tag list is $tag_list_file"

    # Loop through both files simultaneously to create the "image:tag" 
    while read -r image <&3 && read -r tag <&4; do

        echo "Deleting temp files and images from $customer"

        # Customize the content as needed
        docker image rm $harbor_registry/$customer/${image}:${tag} 

    done 3< "$image_list_file" 4< "$tag_list_file"

    rm /tmp/$customer*

}

get_summary() {
    grab_images
    echo "the customer is $customer"
    echo "the image list is $image_list_file"
    echo "the tag list is $tag_list_file"

    # Loop through both files simultaneously to create the "image:tag" 
    while read -r image <&3 && read -r tag <&4; do

        # Create image summary for each image
        summary="$customer-summary-$current_date.txt"

        echo "Creating summary for $customer"

        # Customize the content as needed
        echo ${image} >> "$summary"
        docker pull $harbor_registry/$customer/${image}:${tag} 
        docker inspect $harbor_registry/$customer/${image}:${tag} | jq -r '.[] | "Author: \(.Author), USER: \(.Config.User), CMD: \(.Config.Cmd)"' >> "$summary"
        #docker image rm $harbor_registry/$customer/${image}:${tag} 
        echo -e "" >> "$summary"
        # Add other Dockerfile instructions as needed

    done 3< "$image_list_file" 4< "$tag_list_file"
}

create_dockerfile(){
   grab_images
   # Loop through both files simultaneously to create the "image:tag" 
   while read -r image <&3 && read -r tag <&4; do

      # Create Dockerfile for each image
      dockerfile="${image}.dockerfile"

      echo "Created Dockerfile for $image"

      # Customize the content as needed
      echo "FROM $harbor_registry/$customer/${image}:${tag}" > "$dockerfile"
      # Add other Dockerfile instructions as needed

   done 3< "$image_list_file" 4< "$tag_list_file"
}

update_pipeline(){
   imageList_check
   # Append pipeline manifest to add containers and component_id sections
   echo -e "" >> pipeline-manifest.yaml
   echo "containers:" >> pipeline-manifest.yaml

   while IFS= read -r image || [ -n "$image" ]; do

      echo "  ${image}: ${image}.dockerfile" >> pipeline-manifest.yaml

   done < "$image_list_file"


   echo "component_ids:" >> pipeline-manifest.yaml

   while IFS= read -r image || [ -n "$image" ]; do

      echo ""
      echo "  ${image}:" >> pipeline-manifest.yaml

   done < "$image_list_file"
}

# Set the customer variable
# Ask the user for their name
echo "Please enter customer:"
read customer

# Harbor Username
# Ask the user for their name
echo "Please enter harbor user:"
read harbor_user

# Harbor Password
# Ask the user for their name
unset token
echo "Please enter harbor user token:"
while IFS= read -r -s -n1 token; do
  if [[ -z $token ]]; then
     echo
     break
  else
     echo -n '*'
     harbor_token+=$token
  fi
done

# Function to display the menu
function display_menu {
    echo "1) New customer initial setup"
    echo "2) List of user images in harbor"
    echo "3) Summary of image"
    echo "4) Cleanup - Remove docker images and temp files"
    echo "5) Quit"
}

# Function to process the user's choice
function process_choice {
    read -p "Enter your choice: " choice
    case $choice in
        1) 
         create_imageList
         create_dockerfile
         update_pipeline
        ;;
        2) 
        create_imageList 
        copy_list
        ;;
        3) get_summary ;;
        4) cleanup ;;
        5|q|Q) exit 0 ;;
        *) echo "Invalid choice. Please try again." ;;
    esac
}

# Main loop
while true; do
    display_menu
    process_choice
done