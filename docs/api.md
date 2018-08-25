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
get:    Q:None          >> [user profile data]
        Q:user_id:int   >> [user {id} profile data]
post:   [user profile data] >> [status] 
put:
        [old_password:str, new_password:str] >> [status]
        [user profile data] >> [status]
```
/accounts/profile/followers/
```
get:    [profile followers]
post:   [follow:int:user_id]    >> [status]
        [unfollow:int:user_id]  >> [status]
```
/accounts/profile/followings/
```
get:    [profile followings]
```

### Social
/social/posts/?Q
```
get:    Q:None          >> [all posts]
        Q:tag:str       >> [posts with that tag]
        Q:user_id:int   >> [user posts]
post:   [post data] >> [status]
```
/social/posts/?Q
```
get:    Q:None          >> [all posts]
        Q:tag:str       >> [posts with that tag]
        Q:user_id:int   >> [user posts]
post:   [post data] >> [status]
```
/social/posts/{post_id}/
```
get:    [post data]
put:    [post data] >> [status]
```
/social/posts/{post_id}/comments/
```
get:    [post all comments]
post:   [comment data] >> [status]
```
/social/posts/{post_id}/comments/{comment_id}/
```
put:    [comment data] >> [status]
delete: [status]
```
/social/tags/?Q
```
get:    Q:None      >> [all tags]
        Q:name:str  >> [tags containing name]
```