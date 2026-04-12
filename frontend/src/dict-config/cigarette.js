export default {
  api: '/api/dict/cigarette',
  title: '卷烟品牌',
  columns: [
    { prop: 'product_code', label: '商品编码', required: true, searchable: true, width: 120 },
    { prop: 'product_name', label: '商品名称', required: true, searchable: true, width: 140 },
    { prop: 'brand_owner', label: '品牌拥有者', searchable: true, width: 140 },
    { prop: 'price_category', label: '价类', width: 100 },
  ],
}
