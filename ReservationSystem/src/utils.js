export function formatDate(isoDate) {
    // Crear un objeto Date a partir de la cadena ISO
    const date = new Date(isoDate);

    // Obtener el año, mes y día
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, '0'); // Los meses son base 0, por lo que se suma 1
    const day = String(date.getUTCDate()).padStart(2, '0'); // PadStart asegura que haya dos dígitos

    // Formatear la fecha en YYYY-MM-DD
    return `${year}-${month}-${day}`;
}