import React from 'react';

// Make sure you have Bootstrap included in your project

interface ArtistProbabilitiesTableProps {
  data: Record<string, number>;
}

const ArtistProbabilitiesTable: React.FC<ArtistProbabilitiesTableProps> = ({ data }) =>  {
  // Assuming `data` is the object containing artist probabilities
  // Convert the object into an array of entries
  const entries = Object.entries(data);

  return (
    <div className="mb-3">
      <table className="table">
        <thead>
          <tr>
            <th>Artist</th>
            <th>Similarity</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([artistName, probability]) => (
            <tr key={artistName}>
              <td>{artistName}</td>
              <td>{`${(probability).toFixed(2)}`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ArtistProbabilitiesTable;
