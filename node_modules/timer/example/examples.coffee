
require.paths.unshift __dirname
{timer} = require '../timer.js'



# with coffeescript the utility functions are even more handy

timer 200, -> console.log 'hello'

timer [500,200], -> console.log 'hello after 500ms and 700ms'

# BONG every 30min at even time slots (0:00, 0:30, ..)
{clear} = timer.auto 10*1000, -> console.log 'BONG', +new Date
# end the BONG interval after 5h
timer 20*1000, clear

return


## simple usage:
do ->
	# say hello after 150ms
	timer 150, -> console.log 'hello'
	# same as
	setTimeout (-> console.log 'hello #2'), 150



	# say hello world every 200ms, end after 1500ms
	{clear} = timer null,200, -> console.log 'hello world'
	timer 1500,clear

	# same as
	clear2 = setInterval (-> console.log 'hello world #2'),200
	setTimeout (-> clearInterval clear2),1500





## advanced usage: (start it after 2sec)
timer 2000, ->
	
	# say hello you after 100ms, after 250ms and after 450ms - would say hello you after 950ms again, but this one is stopped (see below)
	{clear} = timer [100,150,200,500], -> console.log (Date.now()%60000)+': hello you'

	# stop above timer after 800ms
	timer 800, clear


	# say BONG every 1min at even times ( 0:00:00, 0:01:00, 0:02:00, ...)
	ret = timer {auto:1}, 60000, -> console.log 'BONG: ' + new Date
	
	# also possible if you want to aboid the braces
	# timer undefined, 6000, -> console.log 'BONG: ' + new Date
	
	# clear the timer after 1 hour	
	timer 60000*60, ret.clear

	# or alternatively:
	# {clearTimer} = require '../timer.js'
	# timer 60000*60,  -> clearTimer ret