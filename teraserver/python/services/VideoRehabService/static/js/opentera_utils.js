function pathJoin(parts, sep){
  let separator = sep || '/';
  let replace  = new RegExp(separator+'{1,}', 'g');
  return parts.join(separator).replace(replace, separator);
}

function calculateContainsWindow(image){
  const imageComputedStyle = window.getComputedStyle(image);
  const imageObjectFit = imageComputedStyle.getPropertyValue("object-fit");
  let coordinates = {};
  const imagePositions = imageComputedStyle.getPropertyValue("object-position").split(" ");
  let naturalWidth = image.naturalWidth;
  let naturalHeight = image.naturalHeight;

  if( image.tagName === "VIDEO" ) {
    naturalWidth= image.videoWidth;
    naturalHeight= image.videoHeight;
  }
  const horizontalPercentage = parseInt(imagePositions[0]) / 100;
  const verticalPercentage = parseInt(imagePositions[1]) / 100;
  const naturalRatio = naturalWidth / naturalHeight;
  const visibleRatio = image.clientWidth / image.clientHeight;

  if (imageObjectFit === "none")
  {
    coordinates.sourceWidth = image.clientWidth;
    coordinates.sourceHeight = image.clientHeight;
    coordinates.sourceX = (naturalWidth - image.clientWidth) * horizontalPercentage;
    coordinates.sourceY = (naturalHeight - image.clientHeight) * verticalPercentage;
    coordinates.destinationWidthPercentage = 1;
    coordinates.destinationHeightPercentage = 1;
    coordinates.destinationXPercentage = 0;
    coordinates.destinationYPercentage = 0;
  }
  else if (imageObjectFit === "contain" || imageObjectFit === "scale-down")
  {
    // TODO: handle the "scale-down" appropriately, once its meaning will be clear
    coordinates.sourceWidth = naturalWidth;
    coordinates.sourceHeight = naturalHeight;
    coordinates.sourceX = 0;
    coordinates.sourceY = 0;
    if (naturalRatio > visibleRatio)
    {
      coordinates.destinationWidthPercentage = 1;
      coordinates.destinationHeightPercentage = (naturalHeight / image.clientHeight) / (naturalWidth / image.clientWidth);
      coordinates.destinationXPercentage = 0;
      coordinates.destinationYPercentage = (1 - coordinates.destinationHeightPercentage) * verticalPercentage;
    }
    else
    {
      coordinates.destinationWidthPercentage = (naturalWidth / image.clientWidth) / (naturalHeight / image.clientHeight);
      coordinates.destinationHeightPercentage = 1;
      coordinates.destinationXPercentage = (1 - coordinates.destinationWidthPercentage) * horizontalPercentage;
      coordinates.destinationYPercentage = 0;
    }
  }
  else if (imageObjectFit === "cover")
  {
    if (naturalRatio > visibleRatio)
    {
      coordinates.sourceWidth = naturalHeight * visibleRatio;
      coordinates.sourceHeight = naturalHeight;
      coordinates.sourceX = (naturalWidth - coordinates.sourceWidth) * horizontalPercentage;
      coordinates.sourceY = 0;
    }
    else
    {
      coordinates.sourceWidth = naturalWidth;
      coordinates.sourceHeight = naturalWidth / visibleRatio;
      coordinates.sourceX = 0;
      coordinates.sourceY = (naturalHeight - coordinates.sourceHeight) * verticalPercentage;
    }
    coordinates.destinationWidthPercentage = 1;
    coordinates.destinationHeightPercentage = 1;
    coordinates.destinationXPercentage = 0;
    coordinates.destinationYPercentage = 0;
  }
  else
  {
    if (imageObjectFit !== "fill")
    {
      console.error("unexpected 'object-fit' attribute with value '" + imageObjectFit + "' relative to");
    }
    coordinates.sourceWidth = naturalWidth;
    coordinates.sourceHeight = naturalHeight;
    coordinates.sourceX = 0;
    coordinates.sourceY = 0;
    coordinates.destinationWidthPercentage = 1;
    coordinates.destinationHeightPercentage = 1;
    coordinates.destinationXPercentage = 0;
    coordinates.destinationYPercentage = 0;
  }
  return coordinates;
}

function include(filename)
{
  let head = document.getElementsByTagName('head')[0];

  let script = document.createElement('script');
  script.src = filename;
  script.type = 'text/javascript';

  head.appendChild(script)
}