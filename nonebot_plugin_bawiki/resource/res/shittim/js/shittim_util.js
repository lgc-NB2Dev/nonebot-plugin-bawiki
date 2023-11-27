() => {
  // 删除顶栏 侧边栏
  document.querySelector('.top-bar').remove();
  document.querySelector('.left-menu').remove();

  // 删除总体星级
  const headList = document.querySelector('.head-list');
  headList.previousElementSibling.remove();
  headList.remove();
};
