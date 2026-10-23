import { useEffect, useState } from "react"

function App() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    fetch("http://127.0.0.1:8000/products")
      .then((response) => response.json())
      .then((data) => {
        setProducts(data)
      })
      .catch((error) => {
        console.error("Error fetching products:", error)
      })
  }, [])

  return (
    <div>
      <h1>Product Store</h1>

      {products.map((product) => (
        <div key={product.id}>
          <img
            src={product.image}
            alt={product.name}
            width="180"
          />

          <h2>{product.name}</h2>

          <p>Price: ₹{product.price}</p>

          <hr />
        </div>
      ))}
    </div>
  )
}

export default App