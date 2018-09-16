* https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7 
* https://tutos.readthedocs.io/en/latest/source/ndg.html
* https://django-best-practices.readthedocs.io/en/latest/deployment/servers.html
* https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-centos-7



used for configuring server and must be doc later.

## MySQL
#### installing mysql 
```
wget https://dev.mysql.com/get/mysql57-community-release-el7-9.noarch.rpm
sudo rpm -ivh mysql57-community-release-el7-9.noarch.rpm
sudo yum install mysql-server
```
#### starting mysql
```
sudo systemctl start mysqld
```
#### getting default password
```
sudo grep 'temporary password' /var/log/mysqld.log
```
#### configuring mysql
```
sudo mysql_secure_installation
```
#### testing mysql
```
mysqladmin -u root -p version
```
#### adding new user
```mysql
CREATE USER 'aasmpro'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'aasmpro'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```
#### connecting using new user
```
sudo mysqladmin -p -u user
```
getting users list
```mysql
SELECT user,authentication_string,plugin,host FROM mysql.user;
```
changing user password
```mysql
ALTER USER 'aasmpro'@'hostname' IDENTIFIED BY 'new_password';
```
#### creating new database
```mysql
CREATE DATABASE akaskhoone CHARACTER SET UTF8;
```
also for deleting
```mysql
DROP DATABASE akaskhoone;
```
#### django DB settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'akaskhoone',
        'USER': 'aasmpro',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```