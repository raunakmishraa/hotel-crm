// Frontend helper: the public hotel configuration and room data are available
// through the Django API. This keeps business details out of HTML.
async function loadHotelConfig() {
  const response = await fetch("/api/v1/hotel/");
  if (!response.ok) throw new Error("Unable to load hotel configuration");
  return response.json();
}

async function loadRooms() {
  const response = await fetch("/api/v1/rooms/");
  if (!response.ok) throw new Error("Unable to load rooms");
  return response.json();
}
