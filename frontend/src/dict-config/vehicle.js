export default {
  api: '/api/dict/vehicle',
  title: '车辆管理',
  columns: [
    { prop: 'plate_number', label: '车牌号', required: true, searchable: true, width: 120 },
    { prop: 'model', label: '车型', searchable: true, width: 100 },
    { prop: 'driver_id', label: '驾驶员', type: 'select', width: 100,
      options: { api: '/api/dict/person/options' } },
    { prop: 'vehicle_type', label: '车辆类型', width: 100,
      type: 'enum', choices: ['油车', '新能源'] },
    { prop: 'cargo_size', label: '车厢大小', width: 100 },
    { prop: 'tank_or_battery_size', label: '油箱/电池容量', type: 'number', width: 130 },
    { prop: 'mileage', label: '行驶里程(km)', type: 'number', width: 120 },
    { prop: 'status', label: '状态', width: 80,
      type: 'enum', choices: ['在用', '停用', '维修'] },
  ],
}
