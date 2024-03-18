import AudioUploader from "./components/AudioUploader";
import ListGroup from "./components/ListGroup";


function App() {
  const items = ['New York', 'San Francisco', 'Tokyo', 'London', 'Paris']
  const handleSelectItem = (item: String) => {
    console.log(item)
  }
  // return <div><ListGroup items={items} heading="Cities" onSelectItem={handleSelectItem}/></div>
  return <div><AudioUploader/></div>
}

export default App