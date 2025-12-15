'use client';

import { Container, Title, Text, SimpleGrid, Card, Image, Button, Group, FileButton, Stack, Loader, Badge, Modal, ActionIcon, Grid } from '@mantine/core';
import { Upload, Trash, Wand2, Download, Eye, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useDisclosure } from '@mantine/hooks';
import { useCart, Product } from '../../context/CartContext';
import Link from 'next/link';

interface SavedFit {
    id: number;
    productId: string;
    productName: string;
    imageUrl: string;
    date: string;
}

export default function CartPage() {
    const { cart, removeFromCart, personImage, setPersonImage } = useCart();

    // Track loading/result state per product ID
    const [loadingItems, setLoadingItems] = useState<Record<string, boolean>>({});
    const [results, setResults] = useState<Record<string, string>>({});

    // Gallery State
    const [gallery, setGallery] = useState<SavedFit[]>([]);
    const [opened, { open, close }] = useDisclosure(false);

    // Load Gallery on Mount
    useEffect(() => {
        const saved = localStorage.getItem('ai_studio_gallery');
        if (saved) {
            try {
                setGallery(JSON.parse(saved));
            } catch (e) {
                console.error("Gallery load error", e);
            }
        }
    }, []);

    // Save Image to Gallery
    const saveToGallery = (product: Product, resultUrl: string) => {
        const newFit: SavedFit = {
            id: Date.now(),
            productId: product.id,
            productName: product.name,
            imageUrl: resultUrl,
            date: new Date().toLocaleDateString()
        };
        const updated = [newFit, ...gallery];
        setGallery(updated);
        localStorage.setItem('ai_studio_gallery', JSON.stringify(updated));
        alert("내 앨범에 저장되었습니다!");
    };

    const deleteFromGallery = (id: number) => {
        const updated = gallery.filter(item => item.id !== id);
        setGallery(updated);
        localStorage.setItem('ai_studio_gallery', JSON.stringify(updated));
    };

    const handleTryOn = async (product: Product) => {
        if (!personImage) {
            alert("먼저 본인의 사진을 업로드해주세요!");
            return;
        }

        setLoadingItems(prev => ({ ...prev, [product.id]: true }));

        const formData = new FormData();
        formData.append('product_id', product.id);
        formData.append('person_image', personImage);
        formData.append('seed', "42");
        formData.append('steps', "30");

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://110.8.186.32:8000';
            const res = await fetch(`${apiUrl}/api/try-on`, {
                method: 'POST',
                body: formData,
            });
            const data = await res.json();
            if (data.success) {
                setResults(prev => ({ ...prev, [product.id]: data.result_url }));
            } else {
                alert(product.name + " 오류: " + data.error);
            }
        } catch (e) {
            console.error(e);
            alert("AI 서버 연결 실패");
        } finally {
            setLoadingItems(prev => ({ ...prev, [product.id]: false }));
        }
    };

    return (
        <Container size="md" py="xl">
            {/* Header */}
            <Group justify="space-between" mb="xs">
                <Title order={2}>장바구니 & 피팅룸</Title>
                <Link href="/" passHref>
                    <Button variant="subtle" size="sm">← 쇼핑 계속하기</Button>
                </Link>
            </Group>

            <Group justify="flex-end" mb="xl">
                <Button
                    variant="outline"
                    color="dark"
                    leftSection={<Eye size={16} />}
                    onClick={open}
                    size="sm"
                >
                    내 앨범 보기 ({gallery.length})
                </Button>
            </Group>

            {/* 1. Global Person Image Uploader (Ultra Compact) */}
            <Card withBorder padding="xs" radius="md" mb="xl" bg="gray.0">
                <Group justify="space-between">
                    <Group gap="sm">
                        <Title order={5} ml="xs">내 사진</Title>
                        <Text size="xs" c="dimmed">이 사진으로 모든 옷을 입어봅니다.</Text>
                    </Group>

                    <Group>
                        {personImage ? (
                            <>
                                <Image
                                    src={URL.createObjectURL(personImage)}
                                    width={50}
                                    height={50}
                                    radius="xl"
                                    style={{ objectFit: 'cover', border: '2px solid white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
                                    alt="Me"
                                />
                                <FileButton onChange={setPersonImage} accept="image/png,image/jpeg">
                                    {(props) => <Button {...props} variant="light" size="xs" color="gray">변경</Button>}
                                </FileButton>
                            </>
                        ) : (
                            <FileButton onChange={setPersonImage} accept="image/png,image/jpeg">
                                {(props) => (
                                    <Button {...props} leftSection={<Upload size={14} />} size="xs" variant="filled" color="dark">
                                        사진 등록
                                    </Button>
                                )}
                            </FileButton>
                        )}
                    </Group>
                </Group>
            </Card>

            {/* 2. Cart Items */}
            <Title order={4} mb="md" c="dimmed">담은 상품 ({cart.length})</Title>

            {cart.length === 0 ? (
                <Container size="sm" py="xl" ta="center">
                    <Title order={2} mb="md">장바구니가 비어있습니다.</Title>
                    <Text c="dimmed" mb="xl">홈으로 돌아가 AI 피팅을 원하는 옷을 담아주세요.</Text>
                    <Link href="/" passHref>
                        <Button variant="filled" color="dark" size="md">
                            AI Studio 구경하기
                        </Button>
                    </Link>
                </Container>
            ) : (
                <SimpleGrid cols={{ base: 1 }} spacing="md">
                    {cart.map((product) => (
                        <Card key={product.id} shadow="sm" padding="md" radius="md" withBorder>
                            <Group align="flex-start" wrap="nowrap">
                                {/* Product Info */}
                                <div style={{ width: '80px', flexShrink: 0 }}>
                                    <Image src={product.image} radius="sm" alt={product.name} />
                                </div>

                                <div style={{ flex: 1 }}>
                                    <Text fw={700} size="sm">{product.name}</Text>
                                    <Text c="dimmed" size="xs" mb="xs">{product.price.toLocaleString()}원</Text>
                                    <Button
                                        color="red"
                                        variant="subtle"
                                        size="compact-xs"
                                        leftSection={<Trash size={12} />}
                                        onClick={() => removeFromCart(product.id)}
                                    >
                                        삭제
                                    </Button>
                                </div>

                                {/* Fitting Logic */}
                                <Stack align="flex-end" style={{ minWidth: '140px' }}>
                                    {results[product.id] ? (
                                        <Stack align="center" gap="xs">
                                            <div style={{ position: 'relative' }}>
                                                <Image
                                                    src={results[product.id]}
                                                    width={120}
                                                    radius="md"
                                                    alt="Result"
                                                    style={{ border: '2px solid #7048E8' }}
                                                />
                                                <ActionIcon
                                                    color="dark"
                                                    style={{ position: 'absolute', bottom: 5, right: 5 }}
                                                    onClick={() => saveToGallery(product, results[product.id])}
                                                >
                                                    <Download size={14} />
                                                </ActionIcon>
                                            </div>
                                            <Group gap={5}>
                                                <Badge color="grape" size="sm">성공</Badge>
                                                <Button
                                                    size="compact-xs"
                                                    variant="light"
                                                    onClick={() => saveToGallery(product, results[product.id])}
                                                >
                                                    저장
                                                </Button>
                                            </Group>
                                        </Stack>
                                    ) : (
                                        <Button
                                            color="grape"
                                            leftSection={<Wand2 size={14} />}
                                            loading={loadingItems[product.id]}
                                            onClick={() => handleTryOn(product)}
                                            disabled={!personImage}
                                            size="sm"
                                        >
                                            AI 입어보기
                                        </Button>
                                    )}
                                </Stack>
                            </Group>
                        </Card>
                    ))}
                </SimpleGrid>
            )}

            {/* Gallery Modal */}
            <Modal opened={opened} onClose={close} title="나의 AI 피팅 앨범" size="lg" centered>
                {gallery.length === 0 ? (
                    <Text c="dimmed" ta="center" py="xl">저장된 피팅 사진이 없습니다.</Text>
                ) : (
                    <Grid>
                        {gallery.map((item) => (
                            <Grid.Col span={4} key={item.id}>
                                <Card padding="xs" radius="md" withBorder>
                                    <Card.Section>
                                        <Image src={item.imageUrl} height={200} fit="cover" alt="Fit" />
                                    </Card.Section>
                                    <Text size="xs" mt="xs" lineClamp={1}>{item.productName}</Text>
                                    <Text size="xs" c="dimmed">{item.date}</Text>
                                    <Button
                                        color="red"
                                        variant="subtle"
                                        size="compact-xs"
                                        fullWidth
                                        mt="xs"
                                        onClick={() => deleteFromGallery(item.id)}
                                    >
                                        삭제
                                    </Button>
                                </Card>
                            </Grid.Col>
                        ))}
                    </Grid>
                )}
            </Modal>
        </Container>
    );
}
