import boto3

rekognition_client = boto3.client('rekognition', region_name="us-east-1")

ALLOWED_IMAGES = ['graffiti', 'art']
def check_image_rekognition(image):
    """
    Using this function to check if image is graffiti or art
    :param image: The uploading image file
    :return: bool
    """
    # Check if the object_name is given or not, if not, using the file_name as the object_name
    response = rekognition_client.detect_labels(Image={'Bytes': image.read()})

    labels = response['Labels']
    print(f'Found {len(labels)} labels in the image:')
    for label in labels:
      name = label['Name']
      confidence = label['Confidence']
      if name in ALLOWED_IMAGES and confidence > 80:
        return True
    return False