module.exports = {
  apps: [{
    name: 'mint-dashboard',
    script: '/home/nexux/nexux-pro/mint-dashboard-server.cjs',
    cwd: '/home/nexux',
    env: {
      DASHSCOPE_API_KEY: 'sk-f09bf021d56e459686ee3c172449f0c9',
      DASHSCOPE_MODEL: 'qwen-plus',
    },
  }],
};
