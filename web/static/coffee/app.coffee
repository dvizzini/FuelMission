jQuery ->
        class MapView extends Backbone.View
                el: $ '#second-hero'

                # if direction button clicked, then get directions
                events: 'click button#get-directions': 'getDirections'

                # setup services and center on chicago
                initialize: ->
                        _.bindAll @, 'render', 'getDirections', 'fetchPrices', 'fetchZip', 'fetchPath', 'geocodePath', 'appendStation'
                        chicago = new google.maps.LatLng 41.850033, -87.6500523
                        myOptions =
                                center: chicago
                                zoom: 7
                                mapTypeId: google.maps.MapTypeId.ROADMAP
                        @render()
                        @map = new google.maps.Map $('#map-canvas', @el)[0], myOptions
                        @dirService = new google.maps.DirectionsService
                        @dirDisplay = new google.maps.DirectionsRenderer
                        @geocoder = new google.maps.Geocoder()
                        @dirDisplay.setMap @map

                # maybe init should be here instead?
                render: ->
                        'nothing'


                getDirections: () ->
                        @fetchPath @geocodePath

                # gives you all the stations for a zip code
                fetchPrices: (zipCode, cb) ->
                        $.getJSON "http://api.mshd.net?gasprice=#{zipCode}&callback=?",
                                  (response) ->
                                        cb response.item


                # gives you a zip for a lat long
                fetchZip: (latLng, cb) ->
                        @geocoder.geocode
                                latLng: latLng,
                                (response) ->
                                        # this is all pretty damn hacky, but it gets zips
                                        try
                                                response.length
                                        catch error
                                                return
                                        for address in response
                                                comps =  address.address_components
                                                last_comp = comps[comps.length - 1]
                                                zip_code = parseInt(last_comp.short_name)
                                                break unless isNaN(zip_code)
                                        cb zip_code

                # grabs the directions response, stores the route, does the callback
                fetchPath: (cb) ->
                        start = $('#start').val()
                        end = $('#end').val()
                        request =
                                origin: start
                                destination: end
                                travelMode: google.maps.TravelMode.DRIVING
                        @dirService.route request, (result, status) =>
                                @path = result.routes[0]
                                @dirDisplay.setDirections result
                                cb()


                # grabs n_points along the route, geocodes them to zips, then gets gas prices from the zips
                geocodePath: (n_points = 5) ->
                        @path.zips = []
                        n_path = @path.overview_path.length
                        n_skip = Math.round n_path/n_points
                        points = _.map _.range(0,n_path,n_skip), (ind) => @path.overview_path[ind]
                        _.each points, (point) =>
                                @fetchZip point, (zip) =>
                                        @path.zips.push zip
                                        console.log @path.zips
                                        @fetchPrices zip, (stations) =>
                                                _.each stations, @appendStation

                # throw a row in
                appendStation: (station) ->
                        $('tbody').append "<tr><td>#{station.address}</td><td>#{station.regular}</td><td><img src='#{station.img}'/></td></tr>"
        mapView = new MapView