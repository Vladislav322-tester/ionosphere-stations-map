const fs = require('fs')
const path = require('path')

const src = path.resolve(__dirname, '..', 'node_modules', 'cesium', 'Build', 'Cesium')
const dest = path.resolve(__dirname, '..', 'public', 'cesium')

function copyRecursive(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return
  if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true })
  const entries = fs.readdirSync(srcDir, { withFileTypes: true })
  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name)
    const destPath = path.join(destDir, entry.name)
    if (entry.isDirectory()) {
      copyRecursive(srcPath, destPath)
    } else {
      try {
        fs.copyFileSync(srcPath, destPath)
      } catch (e) {}
    }
  }
}

copyRecursive(src, dest)
console.log('Cesium assets copied to', dest)
