# API Guide

## version 0

base api address: `/api/v0/`

in each endpoint response, there would be always a `msg` key that it's value show what happened.
so in this doc `[status]` stands for that data.

### Accounts

/accounts/login/
```
post:   [username:str, password:str] >> [access:str, refresh:str]
```
/accounts/refresh/
```
post:   [refresh:str] >> [access:str]
```
/accounts/verify/
```
post:   [access] >> [access:str]
```
/accounts/profile/?Q
```
get:    Q:None      >> [user profile data]
        Q:id:int    >> [user {id} profile data]
post:   [user profile data] >> [status] 
put:
        [old_password:str, new_password:str] >> [status]
        [user profile data] >> [status]
```


