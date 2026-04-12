export default {
  api: '/api/dict/customer',
  title: '零售客户',
  columns: [
    { prop: 'customer_code', label: '客户编码', required: true, searchable: true, width: 120 },
    { prop: 'customer_name', label: '客户名称', required: true, searchable: true, width: 140 },
    { prop: 'address', label: '客户地址', searchable: true, width: 200 },
    { prop: 'phone', label: '电话', width: 120 },
    { prop: 'settlement_method', label: '结算方式', width: 100 },
    { prop: 'department', label: '所属部门', width: 100 },
    { prop: 'route_id', label: '配送线路', type: 'select', width: 120,
      options: { api: '/api/dict/route/options' } },
    { prop: 'delivery_zone', label: '配送域', width: 100 },
    { prop: 'delivery_order', label: '送货顺序', type: 'number', width: 100 },
    { prop: 'market_type', label: '市场类型', width: 100 },
  ],
}
