export default {
  api: '/api/dict/route',
  title: '线路管理',
  columns: [
    { prop: 'route_code', label: '线路编码', required: true, searchable: true, width: 120 },
    { prop: 'route_name', label: '线路名称', required: true, searchable: true, width: 140 },
    { prop: 'driver_id', label: '驾驶员', type: 'select', width: 100,
      options: { api: '/api/dict/person/options' } },
    { prop: 'deliverer_id', label: '送货员', type: 'select', width: 100,
      options: { api: '/api/dict/person/options' } },
    { prop: 'customer_count', label: '客户数量', type: 'number', width: 100 },
    { prop: 'delivery_count', label: '送货数量', type: 'number', width: 100 },
    { prop: 'delivery_time', label: '送货时间', width: 100 },
    { prop: 'settlement_time', label: '结算时间', width: 100 },
    { prop: 'response_time_calc', label: '响应时间计算', width: 130 },
    { prop: 'toll_fee', label: '过路费', type: 'number', width: 100 },
    { prop: 'delivery_cycle', label: '送货周期', width: 100 },
  ],
}
