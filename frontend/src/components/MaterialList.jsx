function MaterialList({ materials }) {
  return (
    <div className="materials">
      <h2>My Study Materials</h2>

      {materials.length === 0 ? (
        <p>No study materials uploaded yet.</p>
      ) : (
        materials.map((material) => (
          <div className="material-card" key={material.id}>
            <h3>{material.title}</h3>
            <p>{material.original_filename}</p>
            <span>{material.file_type}</span>
          </div>
        ))
      )}
    </div>
  );
}

export default MaterialList;