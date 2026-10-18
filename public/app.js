(() => {
  const money = value => `${Number(value).toLocaleString('ko-KR')}원`;
  const distance = value => `${Number(value).toFixed(2)} km`;
  const time = (date, time) => `${date || '-'} ${time || ''}`.trim();
  const colorFor = (price, min, max) => {
    const ratio = max === min ? 0 : (price - min) / (max - min);
    const hue = Math.round(120 - ratio * 120);
    return `hsl(${hue} 75% 42%)`;
  };
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  fetch('data.json', {cache: 'no-store'}).then(response => {
    if (!response.ok) throw new Error(`data.json ${response.status}`);
    return response.json();
  }).then(data => {
    const stations = data.stations || [];
    const prices = stations.map(s => s.price);
    const min = Math.min(...prices), max = Math.max(...prices);
    const map = L.map('map').setView([data.anchor.latitude, data.anchor.longitude], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap contributors'}).addTo(map);
    L.marker([data.anchor.latitude, data.anchor.longitude]).addTo(map).bindPopup(`<strong>${escapeHtml(data.anchor.name)}</strong><br>${escapeHtml(data.anchor.address)}`);
    const markers = new Map();
    stations.forEach(station => {
      const marker = L.circleMarker([station.latitude, station.longitude], {radius: 9, color: colorFor(station.price, min, max), fillOpacity: .85}).addTo(map);
      marker.bindPopup(`<strong>${escapeHtml(station.name)}</strong><br>${escapeHtml(station.address)}<br>${money(station.price)} · ${distance(station.distance_km)}<br>기준 ${escapeHtml(time(station.trade_date, station.trade_time))}`);
      markers.set(station.id, marker);
    });
    document.querySelector('#summary').textContent = `${data.fuel.name} · 기준점 반경 ${data.metadata.radius_m.toLocaleString()}m · ${stations.length}개 주유소`;
    document.querySelector('#updated').textContent = `조회 ${data.metadata.fetched_at || data.generated_at}`;
    document.querySelector('#station-rows').innerHTML = stations.map(station => `<tr data-id="${escapeHtml(station.id)}"><td>${station.rank}</td><td>${escapeHtml(station.name)}</td><td>${distance(station.distance_km)}</td><td class="price">${money(station.price)}</td><td>${escapeHtml(time(station.trade_date, station.trade_time))}</td></tr>`).join('');
    document.querySelectorAll('#station-rows tr').forEach(row => row.addEventListener('click', () => { const marker = markers.get(row.dataset.id); if (marker) { map.setView(marker.getLatLng(), 15); marker.openPopup(); } }));
    document.querySelector('#status').textContent = `데이터 생성 ${data.generated_at} · 출처 ${data.source}`;
  }).catch(error => { document.querySelector('#summary').textContent = '데이터를 표시할 수 없습니다.'; document.querySelector('#status').textContent = error.message; });
})();
