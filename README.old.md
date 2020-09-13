# helpanto
An assistant with basic natural language processing.
For now the following functionalities are supported:
* translation services (supported by lingvoy module)
* weather services (supported by vetero module)

The functionalities are accessible in natural language and command modes. In the natural language mode helpanto can answer basic questions and do simple commands, for example "Translate hammer to spanish." or "Is it going to rain in London in 3 hours?". 
For more precision you can use the command mode, in which the command has to proceded by ">", for example "> lingvoy --word hammer --slang EN --dlang ES" is equvalent to "Translate hammer from english to spanish."
The syntax is as follows: "> command [options...]". Some options take vales, in such a case those should be given after the option name. All option names must be proceded with "--" prefix.

## lingvoy 
This command provides translation services in helpanto. 

--word <word> 
	Mandatory argument, the word to be translated.
--slang <language code>
	Mandatory argument, source language of the word. Language code consists of two uppercase letters, so EN for English and SV for Swedish.
--dlang <language code>
	Mandatory argument, language the word and examples will be translated to. Values as in --slang.
--example
	Procide examples of usage. If --trans is specified, translation of those examples will also be provided.
--trans
	Translate the word.
--grammar
	Provide available grammar information about the word.

## vetero
Command providing weather information.

--loc <city>
	Mandatory argument, location for the weather information.
--time <value>
	Mandatory argument, time for with weather information is queried. value = -1 indicates query about current weather. Otherwise it should be a UNIX timestamp.
--temp
	Provide information about the temperature.
--precip
	Provide information about precipitation.
--cloud
	Provide information about cloudiness.
--sunrise and --sunset
	Provide information about sunrise and sunset accordingly. Work only with --time value = -1.
--wind
	Provide information about the wind.
--duration
	Meaningful only for positive --time values, length of the period of time for which information is requested in hours.
--desc
	Provide weather description.
