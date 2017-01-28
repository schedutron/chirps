

# load timer via require if possible otherwise it should be in the global scope (browsers)
# TODO need to test loading it via requirejs
if require?
	require.paths.unshift __dirname
	{timer} = require '../timer.js'
else if window?
	{timer} = window
	

assertEqual = (msg,x,y) -> console.error(msg, x, y) if x isnt y
assert = (b,msg) -> console.error msg ? 'assertion failed' if not b

AssertSequence = (msg) -> 
	done = 0
	
	(msg2, ncb...) ->
		msgg  = msg + ':' + msg2
		n = 0 
		(a...) ->
			if ncb.length <= n
				return console.error(msgg, 'TOO MANY INVOCATIONS own/global:', n+1, done+1)
				
			done++
			assertEqual msgg+': real/expected: ', done,ncb[n++]
			
			ncb[n++].apply( this, a ) if typeof ncb[n] is 'function'





## TEST1 - simple timeout functions

do ->
	seq = AssertSequence '#1 timeout functions'
	timer 200, seq 'timer 200',
		3
	setTimeout (seq 'setTimeout',2), 190
	do seq 'filler', 1


	setTimeout (-> 
		seq 'setTimeout',4
	
	
		# test clearing timeouts
		{clear} = timer 10, seq 'timer 10'
		do clear
	
		o = timer 10, seq 'timer 10'
		timer.clear o
		
	
	), 210



## TEST2 - interval functions without a timeout

do ->
	seq = AssertSequence '#2 interval functions'

	{clear} = timer null,50,seq '50ms timer',
		3,5
	
	do seq 'begin',1
	timer 75, seq '1',4
	timer 110, seq '2',6
	timer 110, -> do clear

	o = timer.interval 10,seq '10ms timer - should trigger once', 2
	timer 15, -> timer.clear o



## TEST3 - timeout list and interval
do ->
	seq = AssertSequence '#3 timeout list'
	{clear} = timer [50,30], 40, seq 'timer',   # 50, 80, 120, 160, 200, 240, ...
		2,4,6,8

	timer 30, seq '30ms', 1
	# 50 ms timer
	timer 60, seq '60ms', 3
	# 80 ms timer
	timer 90, seq '90ms', 5
	# 120 ms timer
	timer 130, seq '130ms', 7
	# 160 ms timer
	timer 170, seq '170ms', 9

	timer 165, -> do clear



## TEST4 - auto adjusting interval
do test4 = (i) ->
	seq = AssertSequence '#4.'+(i||0)+' auto adjusting interval'
	j = 1
	{clear} = timer.auto 3000, ->
		do seq 'adjusted interval', ++j
		# 50ms margin is ok
		adj = Date.now() % 3000		
		assert adj < 50 or adj > 2950, 'adjusted interval not ok: '+adj
	do seq 'filler', 1
	timer 6003, ->
		do seq 'end', 4
		do clear
		

timer parseInt(Math.random()*10000), -> test4 i for i in [1..500]

do ->
	seq = AssertSequence '#4 auto adjusting interval'
	j = 1
	{clear} = timer.auto 3000, ->
		do seq 'adjusted interval', ++j
		# 50ms margin is ok
		adj = Date.now() % 3000		
		assert adj < 50 or adj > 2950, 'adjusted interval not ok: '+adj
	do seq 'filler', 1
	timer 6003, ->
		do seq 'end', 4
		do clear



