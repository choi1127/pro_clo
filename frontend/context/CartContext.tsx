'use client';

import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

// Define the Product type here to ensure consistency
export interface Product {
    id: string;
    name: string;
    price: number;
    image: string;
    category: string;
}

interface CartContextType {
    cart: Product[];
    addToCart: (product: Product) => void;
    removeFromCart: (productId: string) => void;
    personImage: File | null;
    setPersonImage: (file: File | null) => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
    const [cart, setCart] = useState<Product[]>([]);
    const [personImage, setPersonImage] = useState<File | null>(null);

    // Helpers for File Persistence
    const fileToBase64 = (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = (error) => reject(error);
        });
    };

    const dataURLtoFile = (dataurl: string, filename: string): File => {
        const arr = dataurl.split(',');
        const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/png';
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new File([u8arr], filename, { type: mime });
    };

    // Load from LocalStorage on Mount
    useEffect(() => {
        const savedCart = localStorage.getItem('ai_studio_cart');
        const savedImage = localStorage.getItem('ai_studio_image');

        if (savedCart) {
            try {
                setCart(JSON.parse(savedCart));
            } catch (e) {
                console.error("Failed to parse cart", e);
            }
        }

        if (savedImage) {
            try {
                // Determine filename (we don't store original name, so generic 'my_photo')
                const file = dataURLtoFile(savedImage, 'my_photo.png');
                setPersonImage(file);
            } catch (e) {
                console.error("Failed to parse image", e);
            }
        }
    }, []);

    // Save Cart to LocalStorage
    useEffect(() => {
        localStorage.setItem('ai_studio_cart', JSON.stringify(cart));
    }, [cart]);

    // Save Image to LocalStorage
    useEffect(() => {
        if (personImage) {
            fileToBase64(personImage).then((base64) => {
                localStorage.setItem('ai_studio_image', base64);
            });
        } else {
            // Only remove if we explicitly set it to null (and loop ran).
            // But be careful on initial load: personImage starts null.
            // We need to distinguish "initial null" vs "user cleared".
            // However, for simplicity here: if persistence exists but state is null AFTER load is done...
            // A safer way is checking if we have 'mounted'.
            // For now, let's just save if it exists. Clearing logic might need a 'clear' function.
            // If user explicitly removes image (not implemented in UI yet), we'd want to removeItem.
            // effectively: if we want to support verify removal, we need a flag.
            // Given the requirement: "Updates"
            // If localstorage has image but state is null, we just loaded (or failed).
            // Let's rely on setPersonImage to be called by user actions to overwrite.
        }
    }, [personImage]);

    const addToCart = (product: Product) => {
        if (!cart.find((p) => p.id === product.id)) {
            setCart([...cart, product]);
        }
    };

    const removeFromCart = (productId: string) => {
        setCart(cart.filter((p) => p.id !== productId));
    };

    return (
        <CartContext.Provider value={{ cart, addToCart, removeFromCart, personImage, setPersonImage }}>
            {children}
        </CartContext.Provider>
    );
}

export function useCart() {
    const context = useContext(CartContext);
    if (context === undefined) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
}
