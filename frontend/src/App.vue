<template>
  <div class="container">
    <div class="header">
      <h1>Wan's Design 後台 / 前台 Demo</h1>
      <el-space wrap>
        <router-link to="/admin/fabrics"><el-button type="primary">布料紀錄</el-button></router-link>
        <router-link to="/admin/products"><el-button type="primary">商品紀錄</el-button></router-link>
        <router-link to="/admin/orders"><el-button type="primary">訂購紀錄</el-button></router-link>
        <router-link to="/fabrics/clearance"><el-button>布料出清(前台)</el-button></router-link>
        <router-link to="/fabrics/show"><el-button>布料展示(前台)</el-button></router-link>
        <router-link to="/products/show"><el-button>商品展示(前台)</el-button></router-link>
      </el-space>
    </div>
    <router-view/>
  </div>
</template>
<script setup>
</script>
