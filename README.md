spacepython
===========

Python version of the <a href="https://github.com/nudgepad/space">Space</a> language. 

Currently support 'get', 'set', 'toJSON', 'clone', 'clear', 'lenght', 'getKeys'

Usage
-------

    from space import Space
    space = Space('name John\nage 29\nfavoriteColors\n blue\n green\n red 1\n')
    print space.toJSON()
    
    returns:
    {"age": "29", "name": "John", "favoriteColors": {"blue": {}, "green": {}, "red": "1"}}
    
    space.get('name') // returns 'John'
    
    space.set('age', '1000') 
    space.get('age') // returns '1000'
    

Also try it <a href="http://spacefulpython.appspot.com/">here</a>    
