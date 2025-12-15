'use client';

import { Container, Title, Text, SimpleGrid, Card, Image, Badge, Button, Group } from '@mantine/core';
import { ShoppingCart } from 'lucide-react';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useCart, Product } from '../context/CartContext';

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const { addToCart, cart } = useCart();

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    fetch(`${apiUrl}/api/products`)
      .then((res) => res.json())
      .then((data) => setProducts(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <Container size="lg" py="xl">
      <Group justify="space-between" mb="xs">
        <Title order={1} style={{ fontWeight: 900 }}>AI Studio</Title>
        <Link href="/cart" passHref>
          <Button variant="subtle" leftSection={<ShoppingCart size={20} />}>
            Cart ({cart.length})
          </Button>
        </Link>
      </Group>
      <Text c="dimmed" mb="xl">2024 Collection with AI Fitting</Text>

      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="lg">
        {products.map((product) => (
          <Card key={product.id} shadow="sm" padding="lg" radius="md" withBorder>
            <Card.Section>
              <Image
                src={product.image}
                height={300}
                alt={product.name}
              />
            </Card.Section>

            <Group justify="space-between" mt="md" mb="xs">
              <Text fw={700}>{product.name}</Text>
              <Badge color="pink" variant="light">NEW</Badge>
            </Group>

            <Text size="sm" c="dimmed">
              {product.price.toLocaleString()} KRW
            </Text>

            <Group mt="md" grow>
              <Link href={`/product/${product.id}`} passHref style={{ flex: 1 }}>
                <Button variant="light" color="gray" fullWidth radius="md">
                  Details
                </Button>
              </Link>
              <Button
                color="dark"
                radius="md"
                onClick={() => addToCart(product)}
              >
                Add to Cart
              </Button>
            </Group>
          </Card>
        ))}
      </SimpleGrid>
    </Container>
  );
}
