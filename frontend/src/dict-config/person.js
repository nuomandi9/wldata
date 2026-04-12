export default {
  api: '/api/dict/person',
  title: '人员管理',
  columns: [
    { prop: 'name', label: '姓名', required: true, searchable: true, width: 100 },
    { prop: 'id_card', label: '身份证号', required: true, width: 180 },
    { prop: 'department', label: '部门', searchable: true, width: 100 },
    { prop: 'position', label: '岗位', searchable: true, width: 100 },
    { prop: 'employment_type', label: '用工类型', width: 100 },
    { prop: 'birth_date', label: '出生年月', type: 'date', width: 120 },
    { prop: 'join_date', label: '进入单位时间', type: 'date', width: 120 },
    { prop: 'school', label: '毕业院校', width: 140 },
    { prop: 'degree', label: '学位', width: 80 },
  ],
}
