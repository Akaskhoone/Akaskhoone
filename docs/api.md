# API Guide

## version 0

base api address: `/api/v0/`

in each endpoint response, based on that it was successful or not, there would be a JSON response with `message` or `error` keyword with following structure.


successful:
```
"message": "SignUp Successful"
```
unsuccessful:
```
"error" : {
    "Username": ["Exist"],
    "Name": ["Numeric", "NotUnicode"]
}
```
also `None` in for queries, mean current user.
### Accounts
/accounts/login/
```
post:   [username:str, password:str] >> [access:str, refresh:str]
```
/accounts/refresh/
```
post:   [refresh:str]   >> [access:str]
```
/accounts/verify/
```
post:   [access:str]    >> [access:str]
```
/accounts/profile/?Q
```
get:    Q:None          >> JSON [username:str, email:str, name:str, bio:str,
                                 followings:int, followers:int, image:str:url]
        Q:username      >> JSON [username:str, email:str, name:str, bio:str,
                                 followings:int, followers:int, image:str:url]
        Q:email         >> JSON [username:str, email:str, name:str, bio:str,
                                 followings:int, followers:int, image:str:url]
        ------------------------------
        error:
            profile: [ NotExist ]
        ------------------------------
        example:
            {
                "username": "aasmpro",
                "email": "aasmpro@admin.com",
                "name": "Abolfazl",
                "bio": "My bio",
                "followers": 2,
                "followings": 3,
                "image": "/media/profile_photos/3/20180422231404.jpg"
            }
-----------------------------------------------------------------        
post:   FORMDATA [email:str, username:str, password:str,
                  name:str, bio:str, image:base64]
        ------------------------------
        success:
            message: user created successfully
        
        error:
            email: [ Exist, NotValid ]
            username: [ Exist, Length, Numeric, NotUnicode ]
            password: [ Common, Length, Numeric, NotUnicode ]
            name: [ Length, Numeric ]
            image: [ Size ]
-----------------------------------------------------------------
put:    JSON [old_password:str, new_password:str]
        ------------------------------
        success:
            message: user password changed
        
        error:
            old_password: [ NotMatch ]
            new_password: [ Common, Length, Numeric, NotUnicode ]
        ------------------------------
        
        FORMDATA [name:str, bio:str, image:base64]
        ------------------------------
        success:
            message: user updated successfully
        
        error:
            name: [ Length, Numeric ]
            image: [ Size ]
```
/accounts/profile/followers/?Q
```
get:    Q:None          >> JSON [ username:str { name:str, followed:bool }, ... ]
        Q:username      >> JSON [ username:str { name:str, followed:bool }, ... ]
        Q:email         >> JSON [ username:str { name:str, followed:bool }, ... ]
        ------------------------------
        error:
            profile: [ NotExist ]
```
/accounts/profile/followings/?Q
```
get:    Q:None          >> JSON [ username:str { name:str, followed:bool }, ... ]
        Q:username      >> JSON [ username:str { name:str, followed:bool }, ... ]
        Q:email         >> JSON [ username:str { name:str, followed:bool }, ... ]
        ------------------------------
        error:
            profile: [ NotExist ]
-----------------------------------------------------------------           
post:   JSON [follow:str:username|email]
        ------------------------------
        success:
            message: followed successfully
        
        error:
            user: [ NotExist ]
        ------------------------------

        JSON [unfollow:str:username|email]
        ------------------------------
        success:
            message: unfollowed successfully
        
        error:
            user: [ NotExist ]
        ------------------------------
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