#!/bin/bash
for i in {1..1000}
do
echo -e '\n'
echo $i
echo -e '\n'
curl --header "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTM2MDU1ODM1LCJqdGkiOiI0Mzg3YWI0ZDNkYWM0OWVmOGY5ZWYzZTQ3NzQwZjEzMyIsInVzZXJfaWQiOjR9.c0E-EXusPvXq9Cv3rrR-GxePD5NABanqbNhbcpLMJVQ" --header "Accept: application/json,text/plain,*/*"  http://192.168.11.190:8000/api/v0/accounts/profile/ | cat >> ~/Desktop/logs.txt

echo -e '\n' >> ~/Desktop/logs.txt
done

