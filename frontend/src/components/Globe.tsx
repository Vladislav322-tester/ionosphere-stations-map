import React, { useEffect, useRef } from 'react'
import type { Station } from '../types/station'

type Props = {
  stations: Station[]
  selectedStationId?: string | null
  onSelect: (id: string) => void
}

export default function Globe({ stations, selectedStationId = null, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const viewerRef = useRef<any>(null)
  const cesiumRef = useRef<any>(null)

  useEffect(() => {
    let mounted = true
    ;(window as any).CESIUM_BASE_URL = '/cesium'

    import('cesium').then((Cesium) => {
      if (!mounted || !containerRef.current) return

      cesiumRef.current = Cesium

      const viewer = new Cesium.Viewer(containerRef.current, {
        timeline: false,
        animation: false,
        geocoder: false,
        sceneModePicker: true,
        baseLayerPicker: false,
        infoBox: false,
        navigationHelpButton: false,
      })

      viewerRef.current = viewer

      // Add stations as small point graphics to reduce visual noise
      stations.forEach((s) => {
        const isSelected = selectedStationId && selectedStationId === s.id
        const status = (s as any).status || ''
        const active = String(status).trim().toLowerCase() === 'активна'
        const closed = String(status).trim().toLowerCase() === 'закрыта'

        const color = isSelected
          ? Cesium.Color.YELLOW
          : active
          ? Cesium.Color.fromCssColorString('#34D399') // green
          : closed
          ? Cesium.Color.fromCssColorString('#9CA3AF') // gray
          : Cesium.Color.fromCssColorString('#6B7280') // unknown -> gray

        viewer.entities.add({
          id: s.id,
          name: s.name,
          position: Cesium.Cartesian3.fromDegrees(s.longitude, s.latitude),
          point: {
            pixelSize: isSelected ? 12 : 7,
            color: color,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: isSelected ? 2 : 1,
            scaleByDistance: new Cesium.NearFarScalar(1.5e6, 1.0, 6.0e7, 0.5),
          },
        })
      })

      viewer.zoomTo(viewer.entities)

      viewer.screenSpaceEventHandler.setInputAction((movement: any) => {
        const picked = viewer.scene.pick(movement.position)
        const entity = picked && picked.id

        if (entity && entity.id) {
          onSelect(entity.id)
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK)
    })

    return () => {
      mounted = false

      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy()
      }
    }
  }, [])

  // Rebuild entities when stations or selection changes
  useEffect(() => {
    const viewer = viewerRef.current
    const Cesium = cesiumRef.current

    if (!viewer || !Cesium) return

    viewer.entities.removeAll()

    stations.forEach((s) => {
      const isSelected = selectedStationId && selectedStationId === s.id
      const status = (s as any).status || ''
      const active = String(status).trim().toLowerCase() === 'активна'
      const closed = String(status).trim().toLowerCase() === 'закрыта'

      const color = isSelected
        ? Cesium.Color.CYAN
        : active
        ? Cesium.Color.fromCssColorString('#34D399')
        : closed
        ? Cesium.Color.fromCssColorString('#9CA3AF')
        : Cesium.Color.fromCssColorString('#6B7280')

      viewer.entities.add({
        id: s.id,
        name: s.name,
        position: Cesium.Cartesian3.fromDegrees(s.longitude, s.latitude),
        point: {
          pixelSize: isSelected ? 12 : 6,
          color: color,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: isSelected ? 2 : 1,
          scaleByDistance: new Cesium.NearFarScalar(1.5e6, 1.0, 6.0e7, 0.5),
        },
      })
    })

    // Do not auto-zoom on updates; keep user camera stable
  }, [stations, selectedStationId])

  return <div ref={containerRef} className="globe-container" />
}