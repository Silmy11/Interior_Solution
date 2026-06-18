document.getElementById('inspectForm').addEventListener('submit', function(e) {
    const partName = document.getElementById('partName').value.trim();
    if (partName.length < 3) {
        e.preventDefault();
        alert('Please enter a valid automotive component name.');
    }
});
