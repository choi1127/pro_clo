'use client';

import { Container, Grid, Image, Title, Text, Button, Group, Card, Loader, Stack, Alert } from '@mantine/core';
import { ShoppingCart, Info } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useCart, Product } from '../../../context/CartContext';

export default function ProductDetail() {
    const params = useParams();
    const [product, setProduct] = useState<Product | null>(null);
    const { addToCart, cart } = useCart();

    // Fetch product info (In a real app, fetch specific ID)
    useEffect(() => {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        fetch(`${apiUrl}/api/products`)
            .then((res) => res.json())
            .then((data) => {
                const found = data.find((p: Product) => p.id === params.id);
                if (found) setProduct(found);
            });
    }, [params.id]);

    if (!product) return <Container my="xl"><Loader /></Container>;

    return (
        <Container size="xl" py="xl">
            <Group justify="space-between" mb="md">
                <Button variant="subtle" fullWidth={false} onClick={() => window.location.href = '/'}>
                    ← 목록으로
                </Button>
                <Link href="/cart" passHref>
                    <Button variant="subtle" leftSection={<ShoppingCart size={20} />}>
                        장바구니 ({cart.length})
                    </Button>
                </Link>
            </Group>

            <Grid gutter="xl">
                {/* Left Column: Visuals */}
                <Grid.Col span={{ base: 12, md: 7 }}>
                    <Card shadow="sm" padding={0} radius="md" withBorder style={{ minHeight: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8f9fa' }}>
                        <Image src={product.image} alt="Original" fit="contain" style={{ maxHeight: '500px' }} />
                    </Card>
                    <Text ta="center" size="sm" c="dimmed" mt="xs">
                        상품 원본 이미지
                    </Text>
                </Grid.Col>

                {/* Right Column: Controls */}
                <Grid.Col span={{ base: 12, md: 5 }}>
                    <Stack gap="lg">
                        <div>
                            <Title order={2}>{product.name}</Title>
                            <Text size="xl" fw={700} mt="xs">{product.price.toLocaleString()} KRW</Text>
                        </div>

                        <Group grow>
                            <Button color="dark" size="md" radius="0">바로 구매</Button>
                            <Button
                                variant="outline"
                                color="dark"
                                size="md"
                                radius="0"
                                onClick={() => addToCart(product)}
                            >
                                장바구니 담기
                            </Button>
                        </Group>

                        <Alert variant="light" color="blue" title="✨ AI 가상 피팅" icon={<Info />}>
                            이 옷이 나에게 어울릴까요? <br />
                            <b>장바구니</b>에 담고 내 사진으로 입어보세요!
                        </Alert>
                    </Stack>
                </Grid.Col>
            </Grid>
        </Container>
    );
}
