function confirmDelete(noteId) {
  if (confirm("Are you sure you want to delete this note?")) {
      fetch("/delete-note", {
          method: "POST",
          body: JSON.stringify({ noteId: noteId }),
      }).then((_res) => {
          window.location.href = "/";
      });
  }
}
