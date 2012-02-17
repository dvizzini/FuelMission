jQuery ->
        class MapView extends Backbone.View

                el: $ '#second-hero'
                events: 'click button': 'getDirections'
                initialize: ->
                        _.bindAll @
                        chicago = new google.maps.LatLng 41.850033, -87.6500523
                        myOptions =
                                center: chicago
                                zoom: 7
                                mapTypeId: google.maps.MapTypeId.ROADMAP
                        @map = new google.maps.Map $('#map-canvas', @el)[0], myOptions
                        @dirService = new google.maps.DirectionsService
                        @dirDisplay = new google.maps.DirectionsRenderer
                        @geocoder = new google.maps.Geocoder()
                        @dirDisplay.setMap @map
                        @render()

                render: ->
                        @el.append '<button class="btn">Get Directions</button>'

                getDirections: ->
                        start = $('#start').val()
                        end = $('#end').val()
                        request =
                                origin: start
                                destination: end
                                travelMode: google.maps.TravelMode.DRIVING
                        @dirService.route request, (result, status) =>
                                path = result.routes[0].overview_path
                                points_to_grab = 3
                                n_path = path.length
                                points = _.map _.range(0,
                                        n_path,
                                        Math.round n_path/points_to_grab),
                                                (ind) ->
                                                        path[ind]
                                zips = []
                                _.each points, (point) =>
                                        @geocoder.geocode
                                                latLng: point, (result) =>
                                                        comps =  result[0].address_components
                                                        last_comp = comps[comps.length - 1]
                                                        zip_code = last_comp.short_name
                                                        zips.push zip_code
                                                        @getStations(zips) if zips.length is points_to_grab
                                @dirDisplay.setDirections result if status is google.maps.DirectionsStatus.OK
                getStations: (zips) ->
                        $.getJSON  '/_get_stations',
                                zips: zips,
                                (data) ->
                                        _.each data.stations, (station) ->
                                                $('tbody').append '<tr><td>' + station.address + '</td><td>' + station.price + '</td></tr>'

        mapView = new MapView