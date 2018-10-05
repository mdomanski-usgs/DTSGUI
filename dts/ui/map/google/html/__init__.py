html="""<!DOCTYPE html>
<html>
  <head>
    <title>DTS GUI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta charset="utf-8">
    <style>
      html, body, #map_canvas {
        margin: 0;
        padding: 0;
        height: 100%;
      }
      .fit {
        z-index: 100;
        position: absolute;
        bottom: 18px;
        right: 10px;
      }
      .marker {
        border-radius: 6px;
      }
      .current-marker {
        border: 2px solid yellow !important;
        z-index: 300;
        border-radius: 8px;
        margin-top: -2px;
        margin-left: -2px;
      }
      button {
        position:absolute;
        width: 150px;
        height: 25px;
        top:88%;
        left:1%;
      }
    </style>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js"></script>
    <script src="http://maps.googleapis.com/maps/api/js?sensor=false"></script>
    <script>
      var CustomMarker = function(latlng,  color, map) {
        this.latlng_ = latlng;
        this.color = color;
    
        // Once the LatLng and text are set, add the overlay to the map.  This will
        // trigger a call to panes_changed which should in turn call draw.
        this.setMap(map);
      };
    
      CustomMarker.prototype = jQuery.extend(new google.maps.OverlayView(),{
            draw: function() {
              var me = this;
          
              // Check if the div has been created.
              var div = this.div_;
              if (!div) {
                // Create a overlay text DIV
                div = this.div_ = document.createElement('DIV');
                // Create the DIV representing our CustomMarker
                div.className = "marker";
                div.style.border = "none";
                div.style.position = "absolute";
                div.style.width = '12px';
                div.style.height = '12px';
                div.style.backgroundColor = this.color;
          
                // Then add the overlay to the DOM
                var panes = this.getPanes();
                panes.overlayImage.appendChild(div);
              }
          
              // Position the overlay 
              var point = this.getProjection().fromLatLngToDivPixel(this.latlng_);
              if (point) {
                div.style.left = point.x - 6 + 'px';
                div.style.top = point.y - 6 + 'px';
              }
            },
          remove: function() {
            // Check if the overlay was on the map and needs to be removed.
            if (this.div_) {
              this.div_.parentNode.removeChild(this.div_);
              this.div_ = null;
            }
          },
          getPosition: function() {
           return this.latlng_;
          } 
      });
      
      window.createMarkers = function(json) {
        coordinates = jQuery.parseJSON(json);
        window.bounds = new google.maps.LatLngBounds();

        if (typeof(window.markers) !== "undefined") {
          $.each(window.markers, function(i, marker){
              marker.remove();
          });
        }
        window.markers = [];

        // Extend window boundaries and push coordinates
        var coord;
          $.each(coordinates, function(key, val){
            coord = new google.maps.LatLng(val.lat,val.lon);
            coord.index = val.i;
            window.bounds.extend(coord);

            window.markers[coord.index] = new CustomMarker(
              coord, '#555555',
              window.map
            );
          });
          window.map.fitBounds(window.bounds);
      };

      var zoomToBounds = function() {
        window.map.fitBounds(window.bounds);
      };

      var setOutline = function(i) {
        jQuery("div.current-marker").removeClass("current-marker");
        marker = window.markers[i];
        jQuery(marker.div_).addClass("current-marker");
      };

      var map;
      jQuery(document).ready(function($){
          var mapOptions = {
            zoom: 15,
            center: new google.maps.LatLng(41.485761, -72.515533),
            mapTypeId: google.maps.MapTypeId.SATELLITE
          };
          map = new google.maps.Map(document.getElementById('map_canvas'),
              mapOptions);

      window.createMarkers(json);

      });
    </script>
  </head>
  <body>
    <div id="map_canvas">
    </div>
    <button class='fit' onclick='zoomToBounds()'>Zoom to Bounds</button>
  </body>
</html>"""