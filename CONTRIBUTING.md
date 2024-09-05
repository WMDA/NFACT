# Introduction
Thank you for considering to contributing to NFACT!
We are always looking for contributions so any new ideas/bug fixes/improvements are welcome to try and make NFACT a better tool.

Before you try and contribute please take time to read this CONTRIBUTING.md. 

## Ground Rules
As a quick aside the internet can be a horrible place, so please be repectful to everyone involved with NFACT. 

## Contributing Code
If you have a new idea for NFACT please open a new issue to discuss the idea there. 

If you want to contribute code, do it on your own fork then put in a merge request. Please in your merge request detail exactly what changes you have made to NFACT. Please also keep merges as short and as focused as possible.

### Style
Code is read more than ran, so NFACT is very strict regarding style. This makes it easier for everyone to understand what the code is doing and makes NFACT better.

As such all contributions must:

**Meet pep8 style guide unless there is a special reason why not.**
It is strongly recommend to use the ruff linter (can be installed along with nfact by installing optional dependencies). A ruff.toml is provided with NFACT.

**Have informative variables names.**

This
```
for subject_matrix in list_of_subjects:
```
and not
```
for i in x:
```
The exception to this is when a letter is a standard mathematical variable name.

**Functions and classes must have doc string and type hints**

Functions should be documented similar to numpy
```
def example_function(variable: str, another_variable: int) -> dict:
    '''
    A function to do ....

    Parameters
    ----------
    variable: str
       This is a variable
    another_variable: int
        This is another variable
    
    Returns
    -------
    dict: dictionary object
        a dictionary of stuff

    '''
```

And classes:
```
class MyClass:

"""
A class to ...

Usage
-----
"""
```

**.py files must not be unecessarly long and have informative names.**

No 10,000 line scripts called functions.py please!

**Avoid any additional imports unless already discussed.**

**Think about readability**
This is really difficult to read and maintain

```
for sub in subject:
    for key, value in subjects_dict:
        if len(value) == 1:
            value = sub
        elif:
           if (len(value) != 2) and (len(value) > 3):
               value = sub +1
            else:
               value = sub +2     
        else:
            key +=1
        
```

### Layout

All functions that are shared across multiple "modules" should got into NFACT_base. If a function is specific to a "module" put it in the module. 


## How to report a bug

What version of NFACT are you using?
What operating system and processor architecture are you using?
What did you do?
What did you expect to see?
What did you see instead? 