![Fontofeelya](http://eibbors.com/p/fontofeelya/logo.png)
===========

Tweak font and color scheme settings on the fly with the only Sublime Text plugin that wants to feel you!

This plugin is very much a work in progress, but if you'd like to mess around with it a bit you can clone the repository into your Sublime Text Packages directory (Packages/Fontofeelya) and run the following commands from the python console:

Font Commands
-------------

*Adjust Font Size*

    ```python
        sublime.run_command('adjust_font_size', {'magn': 1})
    ```
    
This is your basic font size adjustment command, accepting an optional magnitude. There is purposefully no minimum font size enforced for positive results and the incr/decr commands included do not scale as I've found the extra freedom/precision to come in handy. Fontopheliacs will most likely agree, I presume.  
    
Color Scheme Commands
---------------------

*Foreground to Background Glow*

    ```python
        sublime.run_command('fgbg_glow')
        sublime.run_command('fgbg_glow', {'magn': 14})
    ```
    
This will produce effects similar to my Bubububububad... color schemes by automatically applying a slightly opaque background color to match any foreground colors not already configured. Accepts an optional magnitude which will be used for the background alpha. Here is a screenshot applied to Tommorow-Night:
![FGBG Screenshot](http://eibbors.com/p/fontofeelya/fgbg.png)

*Invert Colors*

    ```python
        sublime.run_command('invert_colors')
    ```
    
As excpected, this will invert every color in the current color scheme. Although this tends to mess up error/invalid highlighting, the themes produced can be pretty awesome. Checkity check this screenshot, yo:
![Inverted Screenshot](http://eibbors.com/p/fontofeelya/invert.png)

*Desaturate Colors*

    ```python
        sublime.run_command('desaturate_colors')
    ```
    
For those of you who hate colors or want to reduce a color scheme to grayscale values for another plugin/whatever can use this command.
![Inverted Screenshot](http://eibbors.com/p/fontofeelya/desaturate.png)

*Brighten/Darken Colors*

    ```python
        sublime.run_command('brighten_colors') 
        sublime.run_command('brighten_colors', {'magn': 14})
        sublime.run_command('darken_colors')
        sublime.run_command('darken_colors', {'magn': 90})
    ```
    
Brighten or darken the current color scheme by a certain amount. Defaults to +/- 14, which is roughly a 5% increase or decrease. Screenshot below shows Katzen-Milch -> Brighten a few times -> Darken a few times
![Brighten Darken Screenshot](http://eibbors.com/p/fontofeelya/darkbright.png)

I'm currently merging lots of little plugins into this and will submit to Package Control / Sublime Forums when it's got proper menu/commands and the basic font adjustments added.

Author
------
<3 [Eibbor Srednuas](http://eibbors.com)
