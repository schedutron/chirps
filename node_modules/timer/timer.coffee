
timer = (timeouts,interval,cb) ->
	if cb is undefined
		cb = interval
		interval = null
	
	if typeof timeouts is 'number'
		timeouts = [ timeouts ]
		
	timeouts_l = timeouts?.length or 0
	timeouts_i = 0
	
	entry = clear: -> clearTimer entry
	
	do setup = (call) ->
		do cb if call
		
		if timeouts_i < timeouts_l
			entry.timeout = setTimeout setup, timeouts[timeouts_i++], true
		else if interval?
			delete entry.timeout
			entry.interval = setInterval cb,interval

	return entry


timer.auto = (interval, cb) ->
	return timer interval-Date.now()%interval,interval, cb

timer.interval = (interval,cb) ->
	return timer null,interval,cb


timer.clear = clearTimer = (entry) ->
	if entry?.timeout
		clearTimeout entry.timeout
		delete entry.timeout
	if entry?.interval
		clearInterval entry.interval
		delete entry.interval
	

exports.timer = timer if exports?

define? [], -> {timer}
window.timer=timer if window? 