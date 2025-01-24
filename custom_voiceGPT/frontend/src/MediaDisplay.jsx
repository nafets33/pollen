import React from 'react';

const MediaDisplay = ({ showImage, imageSrc, largeHeight = 100, largeWidth = 100, smallHeight = 40, smallWidth = 40 }) => {
    // Determine the dimensions based on `showImage` status
    const height = showImage ? largeHeight : smallHeight;
    const width = showImage ? largeWidth : smallWidth;
  
    return (
      <div className="p-2" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {/* Always show the image or video at the top center based on `showImage` */}
        <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
          {imageSrc && (
            imageSrc.toLowerCase().endsWith(".mp4") ? (
              <video
                style={{ maxWidth: '100%', borderRadius: '8px', objectFit: 'cover' }}
                height={height}
                width={width}
                controls={showImage} // Only show controls if `showImage` is true
                autoPlay
                loop={false}
                muted
              >
                <source src={imageSrc} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            ) : (
              <img
                src={imageSrc}
                height={height}
                width={width}
                style={{ maxWidth: '100%', borderRadius: '8px', objectFit: 'cover' }}
                alt="Media Preview"
              />
            )
          )}
        </div>
      </div>
    );
  };
  
  export default MediaDisplay;