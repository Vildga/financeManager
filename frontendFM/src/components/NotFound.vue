<template>
  <div class="not-found">
    <h1>404 - Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <router-link to="/">Go Home</router-link>
  </div>
</template>

<style scoped>
.not-found {
  text-align: center;
  margin-top: 50px;
}

h1 {
  font-size: 36px;
  color: #ff5c5c;
}

p {
  font-size: 18px;
  color: #666;
}

a {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background: #626cd6;
  color: white;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
}

a:hover {
  background: #4954d0;
}
</style>
