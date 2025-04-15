import React, { useState, useEffect } from "react";
import axios from "axios";

const EcoBlockDashboard = () => {
    const [materials, setMaterials] = useState([]);
    const [predictedUsage, setPredictedUsage] = useState(null);

    useEffect(() => {
        fetchMaterials();
    }, []);

    const fetchMaterials = async () => {
        try {
            const response = await axios.get("http://localhost:8000/materials");
            setMaterials(response.data);
        } catch (error) {
            console.error("Error fetching materials:", error);
        }
    };

    const predictUsage = async (materialType) => {
        try {
            const response = await axios.get(`http://localhost:8000/predict/${materialType}`);
            setPredictedUsage(response.data);
        } catch (error) {
            console.error("Error predicting material usage:", error);
        }
    };

    return (
        <div className="p-6 bg-gray-100 min-h-screen">
            <h1 className="text-3xl font-bold mb-4">Eco-Block Construction Management</h1>
            <div className="bg-white p-4 rounded shadow">
                <h2 className="text-xl font-semibold mb-2">Material Inventory</h2>
                <table className="w-full border-collapse border border-gray-300">
                    <thead>
                        <tr className="bg-gray-200">
                            <th className="border p-2">Material</th>
                            <th className="border p-2">Quantity</th>
                            <th className="border p-2">Source</th>
                            <th className="border p-2">CO₂ Savings</th>
                            <th className="border p-2">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {materials.map((mat) => (
                            <tr key={mat.id} className="border">
                                <td className="p-2 border">{mat.material}</td>
                                <td className="p-2 border">{mat.quantity}</td>
                                <td className="p-2 border">{mat.source}</td>
                                <td className="p-2 border">{mat.carbon_savings.toFixed(2)} kg</td>
                                <td className="p-2 border">
                                    <button
                                        onClick={() => predictUsage(mat.material)}
                                        className="bg-blue-500 text-white px-3 py-1 rounded"
                                    >
                                        Predict Usage
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {predictedUsage && (
                <div className="mt-4 p-4 bg-green-100 rounded">
                    <h3 className="text-lg font-semibold">Predicted Usage</h3>
                    <p>Material: {predictedUsage.material}</p>
                    <p>Expected Usage: {predictedUsage.predicted_usage} units</p>
                </div>
            )}
        </div>
    );
};

export default EcoBlockDashboard;
