# PortSwigger IDOR Labs

A collection of my writeups and notes from **PortSwigger Web Security Academy** labs focused on **Insecure Direct Object References (IDOR)** and **Broken Access Control**.

The goal of this repository is to build strong practical understanding of how object references are exposed, manipulated, and validated by web applications.

## 🎯 Goal

Develop the ability to identify IDOR/BOLA vulnerabilities across different application patterns, including:

* Query parameters
* Path parameters
* Static file references
* Account identifiers
* API object IDs
* Hidden/unrendered data
* Horizontal privilege escalation
* Vertical privilege escalation

## 🧠 Core Lessons

### IDOR is not limited to `?id=`

An object reference can appear in many places:

```text
/account?id=123
/profile/123
/download/file123.txt
/api/users/123
```

The important question is:

> **Can a user manipulate an object reference to access an object they are not authorized to access?**

### Object reference ≠ vulnerability

Changing:

```text
id=123 → id=124
```

doesn't automatically mean an IDOR exists.

The important part is proving that:

1. `123` refers to one object.
2. `124` refers to another user's object.
3. The application allows unauthorized access to `124`.

### Impact matters

An IDOR exposing a harmless public profile is very different from one exposing:

* Passwords
* Private messages
* Personal information
* Financial information
* Administrative data
* Account-management functionality

## 📚 Resources

* [PortSwigger — Access Control](https://portswigger.net/web-security/access-control)
* [PortSwigger — Insecure Direct Object References](https://portswigger.net/web-security/access-control/idor)
* [OWASP — Insecure Direct Object Reference Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)

## 📈 Progress

**Current focus:** IDOR / Broken Access Control

More labs and writeups will be added as I progress through the Access Control section.

> **Learning principle:** Don't just find the parameter. Understand what object it references, who owns that object, what authorization should exist, and what happens when that authorization fails.

**Tags:** `#PortSwigger` `#IDOR` `#BOLA` `#BrokenAccessControl` `#WebSecurity`
