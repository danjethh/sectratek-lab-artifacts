# Security and data problems

## What to report

- A file that looks like **real device data** or a real person's information.
- A reader that, run on your own files, writes content rather than counts to its output.
- A vulnerability in code that processes untrusted input (for example a crafted SQLite or archive).

## How

E-mail daniel@prudentialassociates.com with the report number, the file and a short description. Please do not attach the data itself and do not open a public issue with it.

The Lab will confirm receipt, remove the material from the repository if it should not be there, and say what was done.

## Scope note

The code in this repository is research code run on invented data. It is not hardened for hostile input unless a package README says so. Do not run it on files you do not control without isolation.
