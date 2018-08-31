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
* authorization needed endpoints are labeled with `protected` in this document.
* for request with `Get` method, `Q:None` for queries, mean current user that authorization header specify.
### Accounts
/accounts/login/ 
```
post:   JSON { username:str, password:str } >> JSON { access:str, refresh:str }
```
/accounts/refresh/
```
post:   JSON { refresh:str }    >> JSON { access:str }
```
/accounts/verify/
```
post:   JSON { access:str }     >> JSON { access:str }
```
/accounts/signup/
```    
post:   FORMDATA { email:str, username:str, password:str, name:str, bio:str, image:base64 }
        ------------------------------
        success:
            message: user created successfully
        
        error:
            email:      [ Exist, NotValid ]
            username:   [ Exist, Length, Numeric, NotUnicode ]
            password:   [ Common, Length, Numeric, NotUnicode ]
            name:       [ Length, Numeric ]
            image:      [ Size ]
```
/accounts/profile/?Q `protected`
```
get:    Q:None          >> JSON { username:str, email:str, name:str, bio:str, followings:int, followers:int, image:str:url }
        Q:username      >> JSON { username:str, email:str, name:str, bio:str, followings:int, followers:int, image:str:url }
        Q:email         >> JSON { username:str, email:str, name:str, bio:str, followings:int, followers:int, image:str:url }
        ------------------------------
        error:
            profile:    [ NotExist ]
        ------------------------------
        example:
            {
                "username": "aasmpro",
                "email": "aasmpro@admin.com",
                "name": "Abolfazl Amiri",
                "bio": "My bio",
                "followers": 2,
                "followings": 3,
                "image": "/media/profile_photos/3/20180422231404.jpg"
            }
-----------------------------------------------------------------
put:    JSON { old_password:str, new_password:str }
        ------------------------------
        success:
            message: user password changed
        
        error:
            old_password: [ NotMatch ]
            new_password: [ Common, Length, Numeric, NotUnicode ]
        ------------------------------
        
        FORMDATA { name:str, bio:str, image:base64 }
        ------------------------------
        success:
            message: user updated successfully
        
        error:
            name:       [ Length, Numeric ]
            image:      [ Size ]
```
/accounts/profile/followers/?Q `protected`
```
get:    Q:None          >> JSON { username:str { name:str, followed:bool }, ... }
        Q:username      >> JSON { username:str { name:str, followed:bool }, ... }
        Q:email         >> JSON { username:str { name:str, followed:bool }, ... }
        ------------------------------
        error:
            profile:    [ NotExist ]
```
/accounts/profile/followings/?Q `protected`
```
get:    Q:None          >> JSON { username:str { name:str, followed:bool }, ... }
        Q:username      >> JSON { username:str { name:str, followed:bool }, ... }
        Q:email         >> JSON { username:str { name:str, followed:bool }, ... }
        ------------------------------
        error:
            profile:    [ NotExist ]
-----------------------------------------------------------------           
post:   JSON { follow:str:username|email }
        ------------------------------
        success:
            message: followed successfully
        
        error:
            user:       [ NotExist ]
        ------------------------------

        JSON { unfollow:str:username|email }
        ------------------------------
        success:
            message: unfollowed successfully
        
        error:
            user:       [ NotExist ]
```
### Social
/social/posts/?Q `protected`
```
get:    Q:None          >> JSON { post_id:int { creator:str, image:str:url, des:str, location:str, date:str, tags:[ name1, name2, ... ] } , ... } 
        Q:tag           >> JSON { post_id:int { creator:str, image:str:url, des:str, location:str, date:str, tags:[ name1, name2, ... ] } , ... }
        Q:username      >> JSON { post_id:int { creator:str, image:str:url, des:str, location:str, date:str, tags:[ name1, name2, ... ] } , ... }
        Q:email         >> JSON { post_id:int { creator:str, image:str:url, des:str, location:str, date:str, tags:[ name1, name2, ... ] } , ... }
        ------------------------------        
        error:
            tag:        [ NotExist ]
            username:   [ NotExist ]
            email:      [ NotExist ]
-----------------------------------------------------------------
post:   FORMDATA { image:str:url, des:str, location:str, tags:str }
        ------------------------------
        success:
            message: post created successfully
        
        error:
            image:      [ Required ]        
```
/social/posts/{post_id}/ `protected` 
```
get:    JSON { creator:str, image:str:url, des:str, location:str, date:str, tags:[ name1, name2, ... ] }
        ------------------------------
        error:
            post:       [ NotExist ]
-----------------------------------------------------------------
put:    JSON { des:str, location:str, tags:[ name1, name2, ... ] }
        ------------------------------
        success:
            message: post updated successfully
        
        error:
            post:       [ NotFound ]
            location:   [ NotFound ]
-----------------------------------------------------------------
delete: JSON { des:str, location:str, tags:[ name1, name2, ... ] }
        ------------------------------
        success:
            message: post updated successfully
        
        error:
            post:       [ NotFound ]
            location:   [ NotFound ]        
```
/social/tags/?Q `protected`
```
get:    Q:None          >> JSON [ name1, name2, name3, ... ]
        Q:name:str      >> JSON [ name1, name2, name3, ... ]
```