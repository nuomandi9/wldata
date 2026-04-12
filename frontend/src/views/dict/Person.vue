<template>
  <DictTable :config="config" />
</template>

<script setup>
import DictTable from '../../components/DictTable.vue'
import config from '../../dict-config/person.js'
</script>
